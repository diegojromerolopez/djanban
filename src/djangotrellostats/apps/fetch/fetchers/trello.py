from __future__ import unicode_literals, absolute_import

import math
import re
from collections import namedtuple
from datetime import datetime
from datetime import timedelta

import dateutil.parser
import numpy
import pytz
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from trello import ResourceUnavailable
from trello.board import Board as TrelloBoard

from djangotrellostats.apps.boards.models import Label, Card, Board, List
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.fetch.fetchers.base import Fetcher
from djangotrellostats.apps.reports.models import ListReport, MemberReport, CardMovement
from trello import TrelloClient
import shortuuid


# Initialize boards
class Initializer(object):

    def __init__(self, member, debug=True):
        self.member = member
        self.trello_client = self._get_trello_client()
        self.debug = debug

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.member.api_key,
            api_secret=self.member.api_secret,
            token=self.member.token,
            token_secret=self.member.token_secret
        )
        return client

    # Fetch basic information of boards and its lists
    @transaction.atomic
    def init(self, board_uuid=None):
        trello_boards = self.trello_client.list_boards()
        for trello_board in trello_boards:
            if board_uuid is None or board_uuid == trello_board.id:
                board_already_exists = Board.objects.filter(uuid=trello_board.id).exists()
                if not board_already_exists:
                    board_name = trello_board.name
                    board = Board(uuid=trello_board.id, name=board_name,
                                  last_activity_datetime=trello_board.date_last_activity,
                                  public_access_code=shortuuid.ShortUUID().random(length=20).lower(),
                                  creator=self.member)
                    board.save()
                    if self.debug:
                        print("Board {0} successfully created".format(board_name))
                else:
                    board = Board.objects.get(uuid=trello_board.id)
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
                self._fetch_members(board, trello_board)

    # Fetch members of this board
    def _fetch_members(self, board, trello_board):
        trello_members = trello_board.all_members()

        # For each member, check if he/she doesn't exist. In that case, create him/her
        for trello_member in trello_members:

            # If the member does not exist, create it with empty Trello credentials
            try:
                member = Member.objects.get(uuid=trello_member.id)
                if self.debug:
                    print(u"Member {0} already existed ".format(member.trello_username))
            except Member.DoesNotExist:
                member = Member(uuid=trello_member.id, trello_username=trello_member.username,
                                initials=trello_member.initials)
                member.save()
                if self.debug:
                    print(u"Member {0} created".format(member.trello_username))

            # Only add the board to the member if he/she has not it yet
            if not member.boards.filter(uuid=board.uuid).exists():
                member.boards.add(board)


# Fetches a board from Trello
class BoardFetcher(Fetcher):

    # Date format of the actions and comments
    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    # Create a fetcher from a board
    def __init__(self, board, debug=True):
        super(BoardFetcher, self).__init__(board)
        self.initializer = Initializer(self.creator)
        self.trello_client = self.initializer.trello_client
        self.trello_board = TrelloBoard(client=self.trello_client, board_id=self.board.uuid)
        self.trello_board.fetch()
        self.debug = debug

    # Fetch data of this board
    def fetch(self, debug=False):
        if not self._start_fetch():
            return False

        try:
            with transaction.atomic():
                self._truncate()
                self._fetch_labels()
                self._fetch_cards(debug=debug)
                self._create_card_reports()

                self.board.last_fetch_datetime = timezone.now()
                self.board.save()

        except Exception as e:
            raise

        finally:
            self._end_fetch()

    # Fetch the labels of this board
    def _fetch_labels(self):
        trello_labels = self.trello_board.get_labels()
        for trello_label in trello_labels:
            LabelCreator.create(trello_label, self.board)
        self.labels = self.board.labels.all()

    # Return the Trello Cards
    def _fetch_cards(self, debug=False):
        trello_cards = self.trello_board.all_cards()

        trello_movements_by_card = self._fetch_trello_card_movements_by_card()
        trello_comments_by_card = self._fetch_trello_comments_by_card()

        card_fetcher = CardFetcher(self, trello_cards, trello_movements_by_card, trello_comments_by_card)
        self.cards = card_fetcher.fetch()

    # Fetch the cards of this board
    def _create_card_reports(self, debug=False):

        workflows = self.board.workflows.all()

        # List reports
        list_report_dict = {list_.uuid: ListReport(board=self.board, list=list_, forward_movements=0, backward_movements=0)
                            for list_ in self.lists}

        # Member report
        member_report_dict = {member.uuid: MemberReport(board=self.board, member=member) for member in self.members}

        # Card stats computation
        for card in self.cards:

            trello_card = card.trello_card
            for list_ in self.lists:
                list_uuid = list_.uuid
                card_stats_by_list = card.trello_card.stats_by_list[list_uuid]

                if not hasattr(list_report_dict[list_uuid], "times"):
                    list_report_dict[list_uuid].times = []
                list_report_dict[list_uuid].times.append(card_stats_by_list["time"])

                # Update total forward and backward movements
                list_report_dict[list_uuid].forward_movements += card_stats_by_list["forward_moves"]
                list_report_dict[list_uuid].backward_movements += card_stats_by_list["backward_moves"]

            # Label assignment to each card
            label_uuids = trello_card.idLabels
            card_labels = self.labels.filter(uuid__in=label_uuids)
            for card_label in card_labels:
                card.labels.add(card_label)

            # Associate members to this card
            members = self.members.filter(uuid__in=card.member_uuids)
            for member in members:
                card.members.add(member)

            trello_card_member_uuids = card.member_uuids
            num_trello_card_members = len(trello_card_member_uuids)
            for trello_member_uuid in trello_card_member_uuids:

                # Member reports
                member_report = member_report_dict[trello_member_uuid]

                # Increment the number of cards of the member report
                member_report.number_of_cards += 1

                # Forward movements of the cards
                if member_report.forward_movements is None:
                    member_report.forward_movements = 0
                member_report.forward_movements += math.ceil(1. * card.forward_movements / 1. * num_trello_card_members)

                # Backward movements of the cards
                if member_report.backward_movements is None:
                    member_report.backward_movements = 0
                member_report.backward_movements += math.ceil(
                    1. * card.backward_movements / 1. * num_trello_card_members)

                # Inform this member report has data and must be saved
                member_report.present = True

                # Card time
                if not hasattr(member_report, "card_times"):
                    member_report.card_times = []
                if card.time is not None:
                    member_report.card_times.append(card.time)

                # Card spent time
                if not hasattr(member_report, "card_spent_times"):
                    member_report.card_spent_times = []
                if card.spent_time_by_member.get(trello_member_uuid) is not None:
                    member_report.card_spent_times.append(card.spent_time_by_member.get(trello_member_uuid))

                # Card estimated time
                if not hasattr(member_report, "card_estimated_times"):
                    member_report.card_estimated_times = []
                if card.estimated_time_by_member.get(trello_member_uuid) is not None:
                    member_report.card_estimated_times.append(card.estimated_time_by_member.get(trello_member_uuid))

                # Workflow card reports
                for workflow in workflows:
                    workflow.fetch([card])

        # Average and std. deviation of time cards live in this list
        for list_uuid, list_report in list_report_dict.items():
            if hasattr(list_report, "times"):
                list_report.avg_card_time = numpy.mean(list_report.times)
                list_report.std_dev_card_time = numpy.std(list_report.times, axis=0)
            list_report.save()

        # Average and std. deviation of card times by member
        for member_uuid, member_report in member_report_dict.items():
            if hasattr(member_report, "present") and member_report.present:
                # Average and std deviation of the time of member cards
                if len(member_report.card_times) > 0:
                    member_report.avg_card_time = numpy.mean(member_report.card_times)
                    member_report.std_dev_card_time = numpy.std(member_report.card_times)

                # Average and std deviation of the spent time of member cards
                if len(member_report.card_spent_times) > 0:
                    member_report.avg_card_spent_time = numpy.mean(member_report.card_spent_times)
                    member_report.std_dev_card_spent_time = numpy.std(member_report.card_spent_times)

                # Average and std deviation of the estimated time of member cards
                if len(member_report.card_estimated_times) > 0:
                    member_report.avg_card_estimated_time = numpy.mean(member_report.card_estimated_times)
                    member_report.std_dev_card_estimated_time = numpy.std(member_report.card_estimated_times)

                member_report.save()

    # Return the comments of the board grouped by the uuid of each card
    def _fetch_trello_comments_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="commentCard")
        return comments_by_card

    # Return the card movements of the board grouped by the uuid of each card
    def _fetch_trello_card_movements_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="updateCard:idList")
        return comments_by_card

    # Return the actions of the board grouped by the uuid of each card
    def _fetch_trello_actions_by_card(self, action_filter, limit=1000):
        # Fetch as long as there is a result
        actions = []
        must_retry = True
        since = None
        while must_retry:
            actions_i = self.trello_board.fetch_actions(action_filter, limit, since)
            actions += actions_i
            must_retry = len(actions_i) == limit
            if must_retry:
                # We get the maximum date of these actions and use it to paginate,
                # asking Trello to give us the actions since that date
                since = BoardFetcher._get_since_str_from_actions(actions_i)

        # Group actions by card
        actions_by_card = {}
        for action in actions:
            card_uuid = action[u"data"][u"card"][u"id"]
            if card_uuid not in actions_by_card:
                actions_by_card[card_uuid] = []
            actions_by_card[card_uuid].append(action)
        # Return the actions grouped by card
        return actions_by_card

    # Get the since parameter based on the actions we've got. That is, get the max date of the actions and prepare
    # the since parameter adding one microsecond to that date
    @staticmethod
    def _get_since_str_from_actions(actions):
        # Get max date and parse it from ISO format
        max_date_str = BoardFetcher._get_max_date_from_actions(actions)
        max_date = dateutil.parser.parse(max_date_str)
        # Get next possible date (max_date + 1 millisecond)
        since_date = max_date + timedelta(microseconds=1000)
        since_date_str = since_date.strftime(BoardFetcher.DATE_FORMAT)[:-3] + "Z"
        return since_date_str

    # Get the max date of a list of actions
    # We are not sure about the actions order, so each time we make a fetch of the actions of this board, we have to get
    # the max date to make other fetch since that max date
    @staticmethod
    def _get_max_date_from_actions(actions):
        max_date = None
        for action in actions:
            if max_date is None or max_date < action["date"]:
                max_date = action["date"]
        return max_date


# Fetch a card
class CardFetcher(object):

    # Create the card fetcher
    def __init__(self, board_fetcher, trello_cards, trello_movements_by_card, trello_comments_by_card, debug=False):
        self.board_fetcher = board_fetcher
        self.board = board_fetcher.board
        self.trello_cycle_dict = {list_.uuid: True for list_ in self.board_fetcher.cycle_lists}
        self.trello_lead_dict = {list_.uuid: True for list_ in self.board_fetcher.lead_lists}
        self.lists = self.board_fetcher.lists
        self.done_list = self.board_fetcher.lists.get(type="done")
        self.trello_cards = trello_cards
        self.trello_movements_by_card = trello_movements_by_card
        self.trello_comments_by_card = trello_comments_by_card
        self.debug = debug
        self.cards = []

    # Fetch and create a card
    def fetch(self):

        card_dict = {}

        # Definition of the work each thread must do
        # that is the fetch of some cards
        for trello_card in self.trello_cards:
            must_retry = True
            while must_retry:
                try:
                    card_i = self._create(trello_card)
                    if self.debug:
                        print(u"{0} done".format(card_i.uuid))
                    must_retry = False
                    card_dict[card_i.uuid] = card_i
                except ResourceUnavailable:
                    must_retry = True

        self.cards = card_dict.values()

        # Blocking cards
        for card in self.cards:
            blocking_card_urls = card.trello_card.comment_summary.get("blocking_card_urls")
            # For each one of this card's blocking cards, check if it exists and if that's the case,
            # add the blocking card to its blocking cards
            for blocking_card_url in blocking_card_urls:
                if self.board.cards.filter(url=blocking_card_url).exists():
                    blocking_card = self.board.cards.get(url=blocking_card_url)
                    card.blocking_cards.add(blocking_card)

        # Requirements
        for card in self.cards:
            requirement_codes = card.trello_card.comment_summary.get("requirement_codes")
            # For each one of this card's requirements, check if it exists and if that's the case,
            # add this requirement to this card's requirements
            for requirement_code in requirement_codes:
                if self.board.requirements.filter(code=requirement_code).exists():
                    requirement = self.board.requirements.get(code=requirement_code)
                    card.requirements.add(requirement)

        # Card movements
        for card in self.cards:
            movements = self.trello_movements_by_card.get(card.uuid)
            if movements:
                local_timezone = pytz.timezone(settings.TIME_ZONE)
                for movement in movements:
                    source_list = self.board.lists.get(uuid=movement["data"]["listBefore"]["id"])
                    destination_list = self.board.lists.get(uuid=movement["data"]["listAfter"]["id"])
                    movement_type = "forward"
                    if destination_list.position < source_list.position:
                        movement_type = "backward"

                    movement_naive_datetime = datetime.strptime(movement["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    movement_datetime = local_timezone.localize(movement_naive_datetime)
                    card_movement = CardMovement(board=self.board, card=card, type=movement_type,
                                                 source_list=source_list, destination_list=destination_list,
                                                 datetime=movement_datetime)
                    card_movement.save()

        return self.cards

    # Create a card from a Trello Card
    def _create(self, trello_card):
        card = self._factory(trello_card)
        card.save()
        # Creation of the daily spent times
        CardFetcher._create_daily_spent_times(card)
        return card

    # Creation of the daily spent times
    @staticmethod
    def _create_daily_spent_times(card):
        for daily_spent_time in card.trello_card.daily_spent_times:
            daily_spent_time.card = card
            DailySpentTime.add_daily_spent_time(daily_spent_time)

    # Constructs a Card from a Trello Card
    def _factory(self, trello_card):
        trello_card.actions = self.trello_movements_by_card.get(trello_card.id, [])
        trello_card._comments = self.trello_comments_by_card.get(trello_card.id, [])

        # Time a card is in a list
        self._init_trello_card_stats_by_list(trello_card)

        # Comment stats spent and estimated times
        self._init_trello_card_comment_stats(trello_card)

        self._init_trello_card_stats(trello_card)

        # Creates the Card object
        card = self._factory_from_trello_card(trello_card)

        return card

    # Card creation
    def _factory_from_trello_card(self, trello_card):
        list_ = self.board.lists.get(uuid=trello_card.idList)

        local_timezone = pytz.timezone(settings.TIME_ZONE)
        if trello_card.created_date.tzinfo is None or\
                        trello_card.created_date.tzinfo.utcoffset(trello_card.created_date) is None:
            card_creation_datetime = local_timezone.localize(trello_card.created_date)
        else:
            card_creation_datetime = trello_card.created_date

        card = Card(uuid=trello_card.id, name=trello_card.name, url=trello_card.url,
                    short_url=trello_card.short_url, description=trello_card.desc, is_closed=trello_card.closed,
                    position=trello_card.pos, last_activity_datetime=trello_card.dateLastActivity,
                    board=self.board, list=list_, creation_datetime=card_creation_datetime
                    )

        # Store the trello card data for ease of use
        card.trello_card = trello_card

        # Card comments
        comment_summary = trello_card.comment_summary

        # Card spent and estimated times
        card.spent_time = comment_summary["spent"]["total"]
        card.estimated_time = comment_summary["estimated"]["total"]

        # Forward and backward movements
        card.forward_movements = trello_card.forward_movements
        card.backward_movements = trello_card.backward_movements

        # Times
        card.time = trello_card.time
        card.lead_time = trello_card.lead_time
        card.cycle_time = trello_card.cycle_time

        # Spent and estimated time by member
        card.spent_time_by_member = comment_summary["spent"]["by_member"]
        card.estimated_time_by_member = comment_summary["estimated"]["by_member"]

        # Members that play a role in this task
        card_member_uuids = {member_uuid: True for member_uuid in trello_card.idMembers}
        card_member_uuids.update({member_uuid: True for member_uuid in comment_summary["member_uuids"]})
        card.member_uuids = card_member_uuids.keys()

        # Blocking cards

        return card

    # Initialize this card stats
    def _init_trello_card_stats(self, trello_card):
        # Total forward and backward movements of a card
        trello_card.forward_movements = 0
        trello_card.backward_movements = 0
        trello_card.time = 0

        for list_ in self.lists:
            list_uuid = list_.uuid
            card_stats_by_list = trello_card.stats_by_list[list_uuid]

            trello_card.time += card_stats_by_list["time"]

            # Update total forward and backward movements
            trello_card.forward_movements += card_stats_by_list["forward_moves"]
            trello_card.backward_movements += card_stats_by_list["backward_moves"]

        trello_card.lead_time = None
        trello_card.cycle_time = None

        # Cycle and Lead times
        if trello_card.idList == self.done_list.uuid:
            trello_card.lead_time = sum(
                [list_stats["time"] if list_uuid in self.trello_lead_dict else 0 for list_uuid, list_stats in
                 trello_card.stats_by_list.items()])

            trello_card.cycle_time = sum(
                [list_stats["time"] if list_uuid in self.trello_cycle_dict else 0 for list_uuid, list_stats in
                 trello_card.stats_by_list.items()])

    # Compute the stats of this card
    def _init_trello_card_stats_by_list(self, trello_card):
        # Use cache to avoid recomputing this stats
        if hasattr(self, "stats_by_list"):
            return self.stats_by_list

        # Fake class used for passing a list of trello lists to the method of Card stats_by_list
        ListForStats = namedtuple('ListForStats', 'id django_id')
        fake_trello_lists = [ListForStats(id=list_.uuid, django_id=list_.id) for list_ in self.lists]
        fake_trello_list_done = ListForStats(id=self.done_list.uuid, django_id=self.done_list.id)

        # Hash to obtain the order of a list given its uuid
        trello_list_order_dict = {list_.uuid: list_.id for list_ in self.lists}

        # Comparator function
        def list_cmp(list_1, list_2):
            list_1_order = trello_list_order_dict[list_1]
            list_2_order = trello_list_order_dict[list_2]
            if list_1_order < list_2_order:
                return 1
            if list_1_order > list_2_order:
                return -1
            return 0

        trello_card.stats_by_list = trello_card.get_stats_by_list(lists=fake_trello_lists,
                                                                  list_cmp=list_cmp,
                                                                  done_list=fake_trello_list_done,
                                                                  time_unit="hours", card_movements_filter=None)

    # Fetch comments of this card
    def _init_trello_card_comment_stats(self, trello_card):

        total_spent = None
        total_estimated = None
        spent_by_member = {}
        blocking_card_urls = []
        requirement_codes = []
        estimated_by_member = {}
        member_uuids = {}

        # Comment format:
        # {u'type': u'commentCard', u'idMemberCreator': u'56e2ac8e14e4eda06ac6b8fd',
        #  u'memberCreator': {u'username': u'diegoj5', u'fullName': u'Diego J.', u'initials': u'DJ',
        #                     u'id': u'56e2ac8e14e4eda06ac6b8fd', u'avatarHash': u'a3086f12908905354b15972cd67b64f8'},
        #  u'date': u'2016-04-20T23:06:38.279Z',
        #  u'data': {u'text': u'Un comentario', u'list': {u'name': u'En desarrollo', u'id': u'5717fb3fde6bdaed40201667'},
        #            u'board': {u'id': u'5717fb368199521a139712f0', u'name': u'Test', u'shortLink': u'2CGPEnM2'},
        #            u'card': {u'idShort': 6, u'id': u'57180ae1ed24b1cff7f8da7c', u'name': u'Por todas',
        #                      u'shortLink': u'bnK3c1jF'}}, u'id': u'57180b7e25abc60313461aaf'}

        # For each comment, find the desired pattern and extract the spent and estimated times
        trello_card.daily_spent_times = []
        member_dict = {}
        for comment in trello_card.comments:
            comment_content = comment["data"]["text"]

            # Spent and estimated time calculation
            matches = re.match(Card.COMMENT_SPENT_ESTIMATED_TIME_REGEX, comment_content)
            if matches:
                # Member uuid that has made this Plus for Trello Comment
                member_uuid = comment["idMemberCreator"]
                member_uuids[member_uuid] = True

                # Spent time when developing this task
                spent = float(matches.group("spent"))

                # Add to spent by member
                if member_uuid not in spent_by_member:
                    spent_by_member[member_uuid] = 0
                spent_by_member[member_uuid] += spent

                # Add to total spent
                if total_spent is None:
                    total_spent = 0

                total_spent += spent

                # Estimated time for developing this task
                estimated = float(matches.group("estimated"))

                # Add to estimated by member
                if member_uuid not in estimated_by_member:
                    estimated_by_member[member_uuid] = 0
                estimated_by_member[member_uuid] += estimated

                # Add to total estimated
                if total_estimated is None:
                    total_estimated = 0

                total_estimated += estimated

                # Store spent time by member by day
                local_timezone = pytz.timezone(settings.TIME_ZONE)
                date = local_timezone.localize(datetime.strptime(comment["date"],
                                                                 '%Y-%m-%dT%H:%M:%S.%fZ')).date()
                # If Plus for Trello comment informs that the time was spent several days ago, we have to substract
                # the days to the date of the comment
                if matches.group("days_before"):
                    date -= timedelta(days=int(matches.group("days_before")))

                if matches.group("description") and matches.group("description").strip():
                    description = matches.group("description")
                else:
                    description = trello_card.name

                # Use of memoization to achieve a better performance when loading members
                if member_uuid not in member_dict:
                    member_dict[member_uuid] = self.board.members.get(uuid=member_uuid)

                # Creation of daily spent times for this card
                daily_spent_time = DailySpentTime(board=self.board, description=description,
                                                  member=member_dict[member_uuid], date=date,
                                                  spent_time=spent, estimated_time=estimated)

                if not hasattr(trello_card, "daily_spent_times"):
                    trello_card.daily_spent_times = []

                trello_card.daily_spent_times.append(daily_spent_time)

            else:
                # Blocking cards
                matches = re.match(Card.COMMENT_BLOCKED_CARD_REGEX, comment_content, re.IGNORECASE)
                if matches:
                    card_url = matches.group("card_url")
                    blocking_card_urls.append(card_url)

                # Depends on requirement
                else:
                    matches = re.match(Card.COMMENT_REQUIREMENT_CARD_REGEX, comment_content, re.IGNORECASE)
                    if matches:
                        requirement_code = matches.group("requirement_code")
                        requirement_codes.append(requirement_code)

        trello_card.comment_summary = {
            "daily_spent_times": trello_card.daily_spent_times,
            "member_uuids": member_uuids.keys(),
            "spent": {"total": total_spent, "by_member": spent_by_member},
            "estimated": {"total": total_estimated, "by_member": estimated_by_member},
            "blocking_card_urls": blocking_card_urls,
            "requirement_codes": requirement_codes
        }
        return trello_card.comment_summary


# Label creator
class LabelCreator(object):

    # Constructs a label
    @staticmethod
    def factory(trello_label, board):
        return Label(uuid=trello_label.id, name=trello_label.name, color=trello_label.color, board=board)

    # Creates a label
    @staticmethod
    def create(trello_label, board):
        label = LabelCreator.factory(trello_label, board)
        label.save()
        return label
