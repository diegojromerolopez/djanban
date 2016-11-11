# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import re
from collections import namedtuple
from datetime import datetime
from datetime import timedelta

import pytz
from django.conf import settings
from trello import ResourceUnavailable

from djangotrellostats.apps.boards.models import Card, CardComment
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.reports.models import CardMovement


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

        # We are going to mark all current cards as deletable cards. Only the cards that are present in trello.com
        # will be gotten out. Cards that are not in trello.com are assumed to be deleted so they will be here and
        # will be deleted when all the card fetching process is completed.
        self.deleted_cards_dict = {card.uuid : card for card in self.board.cards.all()}

        # Updated cards gotten from trello.com
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

        # Deletion of cards that are not present in trello
        for deleted_card_uuid, deleted_card  in self.deleted_cards_dict.items():
            deleted_card.delete()

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
        # Creation of the comments
        comments = CardFetcher._create_comments(card)
        # Creation of the daily spent times
        CardFetcher._create_daily_spent_times(card, comments)
        return card

    # Create comments of the card
    @staticmethod
    def _create_comments(card):
        card_comments = []

        # {u'type': u'commentCard', u'idMemberCreator': u'56e2ac8e14e4eda06ac6b8fd',
        #  u'memberCreator': {u'username': u'diegoj5', u'fullName': u'Diego J.', u'initials': u'DJ',
        #                     u'id': u'56e2ac8e14e4eda06ac6b8fd', u'avatarHash': u'a3086f12908905354b15972cd67b64f8'},
        #  u'date': u'2016-04-20T23:06:38.279Z',
        #  u'data': {u'text': u'Un comentario', u'list': {u'name': u'En desarrollo', u'id': u'5717fb3fde6bdaed40201667'},
        #            u'board': {u'id': u'5717fb368199521a139712f0', u'name': u'Test', u'shortLink': u'2CGPEnM2'},
        #            u'card': {u'idShort': 6, u'id': u'57180ae1ed24b1cff7f8da7c', u'name': u'Por todas',
        #                      u'shortLink': u'bnK3c1jF'}}, u'id': u'57180b7e25abc60313461aaf'}
        member_dict = {}

        local_timezone = pytz.timezone(settings.TIME_ZONE)

        # Create each one of the comments
        for comment in card.trello_card.comments:

            # Author of the comment loaded using memoization
            member_uuid = comment["idMemberCreator"]
            if member_uuid not in member_dict:
                try:
                    member_dict[member_uuid] = Member.objects.get(uuid=comment["idMemberCreator"])
                # If the member doesn't exist, create it
                except Member.DoesNotExist as e:
                    deleted_member = Member(
                        uuid=comment["idMemberCreator"], trello_username=comment["memberCreator"]["username"],
                        initials=comment["memberCreator"]["initials"]
                    )
                    deleted_member.save()
                    member_dict[member_uuid] = deleted_member

            author = member_dict[member_uuid]

            # Comment uuid
            uuid = comment["id"]

            # Comment content
            content = comment["data"]["text"]

            # Comment creation datetime
            comment_naive_creation_datetime = datetime.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S.%fZ')
            comment_creation_datetime = local_timezone.localize(comment_naive_creation_datetime)

            # Creation of the card comment
            card_comment = CardComment(uuid=uuid, card=card, author=author,
                                       creation_datetime=comment_creation_datetime, content=content)
            card_comment.save()

            # Create card comment list
            card_comments.append(card_comment)

        return card_comments

    # Creation of the daily spent times
    @staticmethod
    def _create_daily_spent_times(card, comments):
        comments_dict = {comment.uuid: comment for comment in comments}
        for daily_spent_time in card.trello_card.daily_spent_times:
            daily_spent_time.card = card
            daily_spent_time.comment = comments_dict[daily_spent_time.uuid]
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

        try:
            card = self.board.cards.get(uuid=trello_card.id)
            card.name = trello_card.name
            card.url = trello_card.url
            card.short_url = trello_card.short_url
            card.description = trello_card.desc
            card.is_closed = trello_card.closed
            card.position = trello_card.pos
            card.last_activity_datetime = trello_card.dateLastActivity,
            card.list = list_
            del self.deleted_cards_dict[card.uuid]
        except Card.DoesNotExist:
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
                    try:
                        member_dict[member_uuid] = self.board.members.get(uuid=member_uuid)
                    # If the member has left the board
                    except Member.DoesNotExist:
                        member_dict[member_uuid] = Member.objects.get(uuid=member_uuid)

                # Creation of daily spent times for this card
                daily_spent_time = DailySpentTime(board=self.board, description=description,
                                                  member=member_dict[member_uuid], date=date,
                                                  uuid=comment["id"],
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
