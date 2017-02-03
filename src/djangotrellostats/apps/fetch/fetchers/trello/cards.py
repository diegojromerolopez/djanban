# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple
from datetime import datetime

import pytz
from django.conf import settings
from trello import ResourceUnavailable

from djangotrellostats.apps.base.utils.datetime import localize_if_needed
from djangotrellostats.apps.boards.models import Card, CardComment
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
        for deleted_card_uuid, deleted_card in self.deleted_cards_dict.items():
            deleted_card.delete()

        # Card movements
        for card in self.cards:
            movements = self.trello_movements_by_card.get(card.uuid)
            if movements:
                # For each card movement, we update its values if needed
                for movement in movements:
                    source_list = self.board.lists.get(uuid=movement["data"]["listBefore"]["id"])
                    destination_list = self.board.lists.get(uuid=movement["data"]["listAfter"]["id"])
                    movement_type = "forward"
                    if destination_list.position < source_list.position:
                        movement_type = "backward"

                    # Dates are in UTC
                    movement_datetime = datetime.strptime(movement["date"], '%Y-%m-%dT%H:%M:%S.%fZ').\
                        replace(tzinfo=pytz.UTC)

                    # Only create card movements that don't exist
                    try:
                        CardMovement.objects.get(board=self.board, card=card, type=movement_type,
                                                 source_list=source_list, destination_list=destination_list,
                                                 datetime=movement_datetime, member__uuid=movement["idMemberCreator"])

                    except CardMovement.DoesNotExist:
                        try:
                            member = self.board.members.get(uuid=movement["idMemberCreator"])
                        except Member.DoesNotExist:
                            member = Member.objects.get(uuid=movement["idMemberCreator"])

                        card_movement = CardMovement(board=self.board, card=card, type=movement_type,
                                                     source_list=source_list, destination_list=destination_list,
                                                     datetime=movement_datetime, member=member)
                        card_movement.save()

                card.update_lead_cycle_time()

        return self.cards

    # Create a card from a Trello Card
    def _create(self, trello_card):
        trello_card.actions = self.trello_movements_by_card.get(trello_card.id, [])
        trello_card._comments = self.trello_comments_by_card.get(trello_card.id, [])

        # Time a card is in a list
        self._init_trello_card_stats_by_list(trello_card)

        self._init_trello_card_stats(trello_card)

        # Creates the Card object
        card = self._create_from_trello_card(trello_card)

        # Creation of the comments
        comments = CardFetcher._create_comments(card)

        card.update_spent_estimated_time()

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

        card_deleted_comments = {comment.uuid: comment for comment in card.comments.all()}

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
            try:
                card_comment = card.comments.get(uuid=uuid)
                card_comment.content = content
                card_comment.blocking_card = None
                del card_deleted_comments[uuid]
            except CardComment.DoesNotExist:
                card_comment = CardComment(uuid=uuid, card=card, author=author,
                                           creation_datetime=comment_creation_datetime, content=content)

            # Check if comment has a blocking card
            blocking_card = card_comment.blocking_card_from_content
            if blocking_card:
                card_comment.blocking_card = blocking_card

            card_comment.save()

            # Create card comment list
            card_comments.append(card_comment)



        # Delete all card comments that are not present in trello.com
        for comment_uuid, comment in card_deleted_comments.items():
            comment.delete()

        for member_uuid, member in member_dict.items():
            if not card.members.filter(uuid=member_uuid).exists():
                card.members.add(member)

        return card_comments

    # Card creation
    def _create_from_trello_card(self, trello_card):
        list_ = self.board.lists.get(uuid=trello_card.idList)

        try:
            card = self.board.cards.get(uuid=trello_card.id)
            card.name = trello_card.name
            card.url = trello_card.url
            card.short_url = trello_card.short_url
            card.description = trello_card.desc
            card.is_closed = trello_card.closed
            card.position = trello_card.pos
            card.list = list_
            del self.deleted_cards_dict[card.uuid]
        except Card.DoesNotExist:
            card = Card(uuid=trello_card.id, name=trello_card.name, url=trello_card.url,
                        short_url=trello_card.short_url, description=trello_card.desc, is_closed=trello_card.closed,
                        position=trello_card.pos, board=self.board, list=list_)

        # Update card dates if needed
        if trello_card.due_date:
            card.due_datetime = localize_if_needed(trello_card.due_date)
        else:
            card.due_datetime = None
        card.creation_datetime = localize_if_needed(trello_card.created_date)
        card.last_activity_datetime = localize_if_needed(trello_card.dateLastActivity)

        # Store the trello card data for ease of use
        card.trello_card = trello_card

        # Forward and backward movements
        card.forward_movements = trello_card.forward_movements
        card.backward_movements = trello_card.backward_movements

        # Times
        card.time = trello_card.time
        card.lead_time = trello_card.lead_time
        card.cycle_time = trello_card.cycle_time

        card.save()

        # Members
        card.members.clear()
        for member_uuid in trello_card.idMembers:
            card.members.add(Member.objects.get(uuid=member_uuid))

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
        ListForStats = namedtuple('ListForStats', 'id django_id name')
        fake_trello_lists = [ListForStats(id=list_.uuid, django_id=list_.id, name=list_.name) for list_ in self.lists]
        fake_trello_list_done = ListForStats(id=self.done_list.uuid, django_id=self.done_list.id, name=self.done_list.name)

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
