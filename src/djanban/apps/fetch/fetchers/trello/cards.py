# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple
from datetime import datetime

import pytz
from dateutil import parser as dateparser
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from trello import ResourceUnavailable

from djanban.apps.base.utils.datetime import localize_if_needed
from djanban.apps.boards.models import Card, CardComment, CardAttachment
from djanban.apps.members.models import Member, TrelloMemberProfile
from djanban.apps.reports.models import CardMovement


# Fetch a card
class CardFetcher(object):

    # Create the card fetcher
    def __init__(self, board_fetcher, trello_cards, trello_movements_by_card, trello_comments_by_card, debug=False):
        self.board_fetcher = board_fetcher
        self.board = board_fetcher.board
        self.trello_cycle_dict = {list_.uuid: True for list_ in self.board_fetcher.cycle_lists}
        self.trello_lead_dict = {list_.uuid: True for list_ in self.board_fetcher.lead_lists}
        self.lists = self.board_fetcher.lists
        try:
            self.done_list = self.board_fetcher.lists.get(type="done")
        # This shouldn't happen, but in case you have two "done" lists take the last one
        except MultipleObjectsReturned:
            self.done_list = self.board_fetcher.lists.filter(type="done")[-1]
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
                    # Check if movement occurs inside the board. Those movements that happen outside the board
                    # that is from/to a list of other board are ignored.
                    # Your users are encouraged to DON'T DO THAT.
                    source_list_exists = self.board.lists.filter(uuid=movement["data"]["listBefore"]["id"])
                    destination_list_exists = self.board.lists.filter(uuid=movement["data"]["listAfter"]["id"])
                    if not source_list_exists or not destination_list_exists:
                        continue

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
                                                 datetime=movement_datetime,
                                                 member__trello_member_profile__trello_id=movement["idMemberCreator"])

                    except CardMovement.DoesNotExist:
                        try:
                            member = self.board.members.get(trello_member_profile__trello_id=movement["idMemberCreator"])
                        except Member.DoesNotExist:
                            member = Member.objects.get(trello_member_profile__trello_id=movement["idMemberCreator"])

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

        # Create attachments
        CardFetcher._create_attachments(card)

        # Creation of the comments
        CardFetcher._create_comments(card)

        # There is some bug in Django that needs to be resolved in the OneToOne relationships
        if not hasattr(card, "valuation_comment"):
            card.valuation_comment = None

        card.update_spent_estimated_time()

        return card

    # Create attachments of the card
    @staticmethod
    def _create_attachments(card):
        card_attachments = []
        card_deleted_attachments = {attachment.uuid: attachment for attachment in card.attachments.all()}
        member_dict = {}

        for trello_attachment in card.trello_card.attachments:
            uuid = trello_attachment["id"]

            try:
                trello_member_id = trello_attachment["idMember"]
                if trello_member_id not in member_dict:
                    member_dict[trello_member_id] = Member.objects.get(trello_member_profile__trello_id=trello_member_id)
                uploader = member_dict[trello_member_id]
            except Member.DoesNotExist:
                uploader = card.creator

            trello_attachment_creation_date = dateparser.parse(trello_attachment["date"])
            try:
                card_attachment = card.attachments.get(uuid=uuid)
                # If there has been any change in the file or even the URL has changed
                if card_attachment.creation_datetime != trello_attachment_creation_date or\
                        card_attachment.external_file_name != trello_attachment["url"]:
                    card_attachment.file = None
                    card_attachment.external_file_name = trello_attachment["name"]
                    card_attachment.external_file_url = trello_attachment["url"]
                del card_deleted_attachments[uuid]
            except CardAttachment.DoesNotExist:
                card_attachment = CardAttachment(uuid=uuid, card=card, uploader=uploader)
                card_attachment.file = None
                card_attachment.external_file_name = trello_attachment["name"]
                card_attachment.external_file_url = trello_attachment["url"]

            card_attachments.append(card_attachment)

            card_attachment.creation_datetime = localize_if_needed(trello_attachment_creation_date)
            card_attachment.save()

        # Delete all card attachments that are not present in trello.com
        for attachment_uuid, attachment in card_deleted_attachments.items():
            attachment.delete()

        return card_attachments

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
            trello_member_id = comment["idMemberCreator"]
            if trello_member_id not in member_dict:
                try:
                    member_dict[trello_member_id] = Member.objects.get(trello_member_profile__trello_id=comment["idMemberCreator"])
                # If the member doesn't exist, create it
                except Member.DoesNotExist as e:
                    deleted_member = Member()
                    deleted_member.save()
                    try:
                        trello_member_profile = TrelloMemberProfile.objects.get(
                            trello_id=comment["idMemberCreator"],
                            username=comment["memberCreator"]["username"],
                            initials=comment["memberCreator"]["initials"]
                        )
                    except TrelloMemberProfile.DoesNotExist:
                        trello_member_profile = TrelloMemberProfile(
                            member=deleted_member,
                            trello_id=comment["idMemberCreator"],
                            username=comment["memberCreator"]["username"],
                            initials=comment["memberCreator"]["initials"]
                        )

                    trello_member_profile.member = deleted_member
                    trello_member_profile.save()

                    member_dict[trello_member_id] = deleted_member

            author = member_dict[trello_member_id]

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
                card_comment = CardComment(uuid=uuid, card=card, board=card.board, author=author,
                                           creation_datetime=comment_creation_datetime, content=content)

            #print "{0} {1} {2}".format(card.name, card_comment.content, card_comment.creation_datetime)

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

        for trello_member_id, member in member_dict.items():
            if not card.members.filter(trello_member_profile__trello_id=trello_member_id).exists():
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

        # Times
        card.lead_time = trello_card.lead_time
        card.cycle_time = trello_card.cycle_time

        card.save()

        # Members
        card.members.clear()
        for trello_member_id in trello_card.idMembers:
            card.members.add(Member.objects.get(trello_member_profile__trello_id=trello_member_id))

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
            list_1_order = trello_list_order_dict.get(list_1)
            list_2_order = trello_list_order_dict.get(list_2)
            if list_1_order is not None and list_2_order is not None:
                if list_1_order < list_2_order:
                    return 1
                if list_1_order > list_2_order:
                    return -1
                return 0
            # In case the movement is from/to a list of other board, ignore it
            return 0

        trello_card.stats_by_list = trello_card.get_stats_by_list(lists=fake_trello_lists,
                                                                  list_cmp=list_cmp,
                                                                  done_list=fake_trello_list_done,
                                                                  time_unit="hours", card_movements_filter=None)
