# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import


import dateutil.parser
import shortuuid
from django.db import transaction
from django.utils import timezone
from trello.board import Board as TrelloBoard

from djangotrellostats.apps.boards.models import Board, List
from djangotrellostats.apps.fetch.fetchers.base import Fetcher
from djangotrellostats.apps.fetch.fetchers.trello.cards import CardFetcher
from djangotrellostats.apps.fetch.fetchers.trello.labels import LabelUpdater
from djangotrellostats.apps.members.models import Member, MemberRole, TrelloMemberProfile
from djangotrellostats.apps.workflows.models import WorkflowCardReport
from djangotrellostats.remote_backends.trello.connector import TrelloConnector


# Initialize boards
class Initializer(TrelloConnector):

    def __init__(self, member, debug=False):
        super(Initializer, self).__init__(member)
        self.debug = debug

    # Fetch basic information of boards and its lists
    @transaction.atomic
    def init(self, board_uuid=None):
        trello_boards = self.trello_client.list_boards()
        # If the member has a maximum numbers of boards, limit the numbers of boards the member can fetch
        if self.member.max_number_of_boards is not None:
            trello_boards = trello_boards[:self.member.max_number_of_boards]

        # For each Trello board, create a new board if it doesn't exist or update the board if it already exists
        for trello_board in trello_boards:
            if board_uuid is None or board_uuid == trello_board.id:
                board_already_exists = Board.objects.filter(uuid=trello_board.id).exists()
                if not board_already_exists:
                    board_name = trello_board.name
                    board = Board(uuid=trello_board.id, name=board_name, description=trello_board.description,
                                  last_activity_datetime=trello_board.date_last_activity,
                                  public_access_code=shortuuid.ShortUUID().random(length=20).lower(),
                                  creator=self.member)
                    board.save()
                    if self.debug:
                        print("Board {0} successfully created".format(board_name))
                else:
                    board = Board.objects.get(uuid=trello_board.id)
                    board_is_updated = False
                    # Change in name
                    if board.name != trello_board.name:
                        board.name = trello_board.name
                        board_is_updated = True
                    # Change in description
                    if board.description != trello_board.description:
                        board.description = trello_board.description
                        board_is_updated = True
                    # Board needs updating
                    if board_is_updated:
                        board.save()
                    # Board name
                    board_name = board.name

                # Fetch all lists of this board
                trello_lists = trello_board.all_lists()
                _lists = []
                last_created_list = None
                for trello_list in trello_lists:

                    if not board.lists.filter(uuid=trello_list.id).exists():
                        _list = List(uuid=trello_list.id, name=trello_list.name, board=board)

                        if trello_list.closed:
                            _list.type = "closed"

                        _list.save()
                        last_created_list = _list

                        if self.debug:
                            print("- List {1} of board {0} successfully created".format(board_name, _list.name))

                    else:
                        _list = board.lists.get(uuid=trello_list.id)
                        if _list.position != trello_list.pos:
                            _list.position = trello_list.pos
                            _list.save()

                        if self.debug:
                            print("- List {1} of board {0} was already created".format(board_name, _list.name))

                    _lists.append(_list)

                # By default, consider the last list as "done" list
                if last_created_list and last_created_list.type != "closed" and not board.lists.filter(type="done").exists():
                    last_created_list.type = "done"
                    last_created_list.save()

                # Fetch all members this board and associate to this board
                self.fetch_members(board, trello_board)

    # Fetch members of this board
    def fetch_members(self, board, trello_board):
        trello_members = trello_board.all_members()

        # For each member, check if he/she doesn't exist. In that case, create him/her
        for trello_member in trello_members:

            # If the member does not exist, create it with empty Trello credentials
            try:
                member = Member.objects.get(trello_member_profile__trello_id=trello_member.id)
                if self.debug:
                    print(u"Member {0} already existed ".format(member.external_username))
            except Member.DoesNotExist:
                member = Member(creator=self.member)
                member.save()
                trello_member_profile = TrelloMemberProfile(
                    trello_id=trello_member.id,
                    member=member, username=trello_member.username, initials=trello_member.initials
                )
                trello_member_profile.save()

                if self.debug:
                    print(u"Member {0} created".format(member.external_username))

            # Only add the board to the member if he/she has not it yet
            if not member.boards.filter(uuid=board.uuid).exists():
                member.boards.add(board)

            if self.debug:
                print(u"Member {0} has role {1}".format(member.external_username, trello_member.member_type))
            # If this member has no role in this board, add the role to the member
            if not member.roles.filter(board=board).exists():
                if self.debug:
                    print("Creating role {0} for {1}".format(trello_member.member_type, board.name))
                member_role, created = MemberRole.objects.get_or_create(board=board, type=trello_member.member_type)
                member_role.members.add(member)

            # If this member has a role but is different from the role he/she has in Trello,
            # update his/her role
            elif member.roles.get(board=board).type != trello_member.member_type:
                if self.debug:
                    print(
                        "Updating {0}'s role from {1} to {2} in {3}".format(
                            member.external_username, member.roles.get(board=board).type,
                            trello_member.member_type, board.name
                        )
                    )
                member.roles.clear()
                member_role, created = MemberRole.objects.get_or_create(board=board, type=trello_member.member_type)
                member_role.members.add(member)

    # Creates a new board from a non-saved board object
    def create_board(self, board, lists=None):
        # Check if board exists
        if board.uuid:
            raise ValueError(u"This board already exists")
        # Connect to Trello and save the new board
        trello_board = TrelloBoard(client=self.trello_client)
        trello_board.name = board.name
        trello_board.description = board.description
        trello_board.save()
        # Trello id attribute assignment
        board.uuid = trello_board.id
        board.save()
        # Creation of lists
        if lists is not None and len(lists) > 0:
            for list_name in lists:
                self.create_list(board, list_name, list_position="bottom")
            # Fetch initial lists
            self.init(board.uuid)

    # Create list for a board
    def create_list(self, board, list_name, list_position="bottom"):
        trello_board = None
        trello_boards = self.trello_client.list_boards()
        for trello_board_i in trello_boards:
            if board.uuid == trello_board_i.id:
                trello_board = trello_board_i
                break

        # Check if this board exist in Trello
        if trello_board is None:
            raise ValueError(u"This board does not exist")

        # Create the new lists
        trello_board.add_list(list_name, list_position)


# Fetches a board from Trello
class BoardFetcher(Fetcher):

    # Date format of the actions and comments
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    # Create a fetcher from a board
    def __init__(self, board, debug=True):
        super(BoardFetcher, self).__init__(board)
        self.initializer = Initializer(self.creator, debug=debug)
        self.trello_client = self.initializer.trello_client
        self.trello_board = TrelloBoard(client=self.trello_client, board_id=self.board.uuid)
        self.initializer.fetch_members(board, self.trello_board)
        self.trello_board.fetch()
        self.debug = debug

    # Fetch data of this board
    def fetch(self, debug=False):
        self._start_fetch()

        try:
            with transaction.atomic():
                self._truncate()
                self._fetch_labels()
                self._fetch_cards(debug=debug)
                self._create_card_reports()

                self.board.last_fetch_datetime = timezone.now()
                self.board.last_activity_datetime = self.board.last_fetch_datetime
                self.board.save()

        except Exception as e:
            raise

        finally:
            self._end_fetch()

    # Fetch the labels of this board
    def _fetch_labels(self):
        trello_labels = self.trello_board.get_labels()
        for trello_label in trello_labels:
            LabelUpdater.update(trello_label, self.board)
        self.labels = self.board.labels.all()

    # Return the Trello Cards
    def _fetch_cards(self, debug=False):
        trello_cards = self.trello_board.all_cards()

        trello_movements_by_card = self._fetch_trello_card_movements_by_card()
        trello_comments_by_card = self._fetch_trello_comments_by_card()

        card_fetcher = CardFetcher(self, trello_cards, trello_movements_by_card, trello_comments_by_card)
        self.cards = card_fetcher.fetch()

    # Fetch the card repots of this board
    def _create_card_reports(self, debug=False):

        workflows = self.board.workflows.all()

        # Card stats computation
        for card in self.cards:

            trello_card = card.trello_card
            for list_ in self.lists:
                list_uuid = list_.uuid
                card_stats_by_list = card.trello_card.stats_by_list[list_uuid]

            # Label assignment to each card
            label_uuids = trello_card.idLabels
            card_labels = self.labels.filter(uuid__in=label_uuids)
            card.labels.clear()
            for card_label in card_labels:
                card.labels.add(card_label)

            num_trello_card_members = card.members.all().count()
            for member in card.members.all():
                member_uuid = member.uuid

                # Workflow card reports
                for workflow in workflows:
                    self._fetch_workflow(workflow, [card])


    # Return the actions of the board grouped by the uuid of each card
    def _fetch_trello_cards(self):
        # Fetch as long as there is a result
        cards = []
        must_retry = True

        # Limit of cards in each request
        limit = 1000

        # We will be making request from the earliest to the oldest actions, so we will use before parameter
        # while since is always None
        filters = {
            'filter': 'all',
            'fields': 'all',
        }

        # While there are more than 1000 cards, make another request for the previous 1000 cards
        while must_retry:
            cards_i = self.trello_board.get_cards(filters=filters)
            cards += cards_i
            must_retry = len(cards_i) == limit
            if must_retry:
                # We get the maximum date of these cards and use it to paginate,
                # asking Trello to give us the actions since that date
                before = BoardFetcher._get_before_str_from_cards(cards_i)
                filters["before"] = before

        # There should be no need to assure uniqueness of the cards but it's better to be sure that
        # we have no repeated actions
        cards_dict = {card.id: card for card in cards}
        unique_cards = cards_dict.values()

        # Return the cards
        return unique_cards

    # Get the since parameter based on the actions we've got. That is, get the max date of the actions and prepare
    # the since parameter adding one microsecond to that date
    @staticmethod
    def _get_before_str_from_cards(cards):
        # Get max date and parse it from ISO format
        min_date_str = BoardFetcher._get_min_date_from_cards(cards)
        min_date = dateutil.parser.parse(min_date_str)
        # Get next possible date (max_date + 1 millisecond)
        before_date = min_date
        before_date_str = before_date.strftime(BoardFetcher.DATE_FORMAT)[:-3] + "Z"
        return before_date_str

    # Get the min date of a list of cards
    @staticmethod
    def _get_min_date_from_cards(cards):
        min_date = None
        for card in cards:
            if min_date is None or min_date > card.created_date:
                min_date = card.created_date
        return min_date

    # Return the comments of the board grouped by the uuid of each card
    def _fetch_trello_comments_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="commentCard", debug=True)
        return comments_by_card

    # Return the card movements of the board grouped by the uuid of each card
    def _fetch_trello_card_movements_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="updateCard:idList")
        return comments_by_card

    # Return the actions of the board grouped by the uuid of each card
    def _fetch_trello_actions_by_card(self, action_filter, limit=1000, debug=False):
        # Fetch as long as there is a result
        actions = []
        must_retry = True

        # We will be making request from the earliest to the oldest actions, so we will use before parameter
        # while since is always None
        since = None
        before = None

        # While there are more than 1000 actions, make another request for the previous 1000 actions
        while must_retry:
            actions_i = self.trello_board.fetch_actions(action_filter, limit, before=before, since=since)
            actions += actions_i
            must_retry = len(actions_i) == limit
            if must_retry:
                # We get the maximum date of these actions and use it to paginate,
                # asking Trello to give us the actions since that date
                before = BoardFetcher._get_before_str_from_actions(actions_i)

        # There should be no need to assure uniqueness of the actions but it's better to be sure that
        # we have no repeated actions
        actions_dict = {action["id"]: action for action in actions}
        unique_actions = actions_dict.values()

        # Group actions by card
        actions_by_card = {}
        for action in unique_actions:
            card_uuid = action[u"data"][u"card"][u"id"]
            if card_uuid not in actions_by_card:
                actions_by_card[card_uuid] = []
            actions_by_card[card_uuid].append(action)

        # Return the actions grouped by card
        return actions_by_card

    # Get the since parameter based on the actions we've got. That is, get the max date of the actions and prepare
    # the since parameter adding one microsecond to that date
    @staticmethod
    def _get_before_str_from_actions(actions):
        # Get max date and parse it from ISO format
        min_date_str = BoardFetcher._get_min_date_from_actions(actions)
        min_date = dateutil.parser.parse(min_date_str)
        # Get next possible date (max_date + 1 millisecond)
        before_date = min_date
        before_date_str = before_date.strftime(BoardFetcher.DATE_FORMAT)[:-3] + "Z"
        return before_date_str

    # Get the min date of a list of actions
    # We are not sure about the actions order, so each time we make a fetch of the actions of this board, we have to get
    # the max date to make other fetch since that max date
    @staticmethod
    def _get_min_date_from_actions(actions):
        min_date = None
        for action in actions:
            if min_date is None or min_date > action["date"]:
                min_date = action["date"]
        return min_date

    # Fetch data for this workflow, creating a workflow report
    def _fetch_workflow(self, workflow, cards):
        workflow_lists = workflow.workflow_lists.all()
        development_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                             workflow.workflow_lists.filter(is_done_list=False)}
        done_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                      workflow.workflow_lists.filter(is_done_list=True)}

        workflow_card_reports = []

        for card in cards:
            trello_card = card.trello_card

            lead_time = None
            cycle_time = None

            # Lead time and cycle time only should be computed when the card is done
            if not card.is_closed and trello_card.idList in done_lists:
                # Lead time in this workflow for this card
                lead_time = sum([list_stats["time"] for list_uuid, list_stats in trello_card.stats_by_list.items()])

                # Cycle time in this workflow for this card
                cycle_time = sum(
                    [list_stats["time"] if list_uuid in development_lists else 0 for list_uuid, list_stats in
                     trello_card.stats_by_list.items()])

                workflow_card_report = WorkflowCardReport(board=self.board, workflow=workflow,
                                                          card=card, cycle_time=cycle_time, lead_time=lead_time)
                workflow_card_report.save()

                workflow_card_reports.append(workflow_card_report)

        return workflow_card_reports

