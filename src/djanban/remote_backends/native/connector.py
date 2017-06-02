# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import random

from django.db.models import Max
from django.urls import reverse
from django.utils import timezone

from djanban.utils.custom_uuid import custom_uuid


# Native connector for board that are not synchronized with Trello or other external platforms
class NativeConnector(object):

    def __init__(self, member):
        self.member = member

    def reconnect(self):
        pass

    # Create a new board
    def new_board(self, board):
        board.uuid = custom_uuid()
        board.has_to_be_fetched = False
        board.last_activity_datetime = timezone.now()
        return board

    def new_label(self, label):
        label.uuid = custom_uuid()
        return label

    # Add existing member to this board
    def add_member(self, board, member_to_add, member_type="normal"):
        pass

    # Delete member from this board
    def remove_member(self, board, member_to_remove):
        pass

    # List operations

    # Move list list_ to the position
    # member is used for authentication
    def move_list(self, list_, position):
        pass

    # Create a new list
    def new_list(self, new_list):
        new_list.uuid = custom_uuid()
        # Calculation of position is a bit tricky:
        # As position of the new list doesn't really matter, and
        # we don't want to block some tuples of the database, we get the max position
        # and add a random offset.
        random_offset = random.randrange(0, 1000)
        position = 0
        if new_list.board.lists.all().exists():
            position = new_list.board.lists.aggregate(max=Max("position"))["max"]
        new_list.position = position + random_offset
        now = timezone.now()
        new_list.creation_datetime = now
        new_list.last_activity_datetime = now
        return new_list

    # Edit a list
    def edit_list(self, edited_list):
        pass

    # Card operations

    # Creates a new card
    def new_card(self, card, labels=None, position="bottom"):
        # Card attribute assignment
        card.uuid = custom_uuid()
        card.short_url = reverse("boards:view_card_short_url", args=(card.board_id, card.uuid))
        card.url = reverse("boards:view_card_short_url", args=(card.board_id, card.uuid))
        # Position is a bit more difficult
        cards = card.list.active_cards.all()
        if not cards.exists():
            position = 100000
        else:
            if position == "top":
                position = cards.order_by("position")[0].position - 1000
            elif position == "bottom":
                position = cards.order_by("-position")[0].position + 1000

        card.position = position
        card.creation_datetime = timezone.now()
        card.last_activity_datetime = timezone.now()
        return card

    # Order card
    def order_card(self, card, position):
        pass

    # Move the card to other list
    def move_card(self, card, destination_list):
        pass

    # Move all cards from a list
    def move_list_cards(self, source_list, destination_list):
        pass

    def add_attachment_to_card(self, card, attachment):
        attachment.card = card
        attachment.uuid = custom_uuid()
        attachment.creation_datetime = timezone.now()
        return attachment

    def delete_attachment_of_card(self, card, attachment):
        return attachment

    # Add comment to a card
    def add_comment_to_card(self, card, comment):
        comment.uuid = custom_uuid()
        comment.last_edition_datetime = None
        return comment

    # Edit comment content
    def edit_comment_of_card(self, card, comment):
        comment.last_edition_datetime = timezone.now()

    # Delete comment of card
    def delete_comment_of_card(self, card, comment):
        pass

    # Add a labels to a card
    def add_label_to_card(self, card, label):
        pass

    # Add a labels to a card
    def remove_label_of_card(self, card, label):
        pass

    # Add a member to a card
    def add_member_to_card(self, card, member_to_add):
        pass

    # Remove member from card
    def remove_member_of_card(self, card, member_to_remove):
        pass

    # Sets the name of the card in Trello
    def set_card_name(self, card):
        pass

    # Sets the description of the card in Trello
    def set_card_description(self, card):
        pass

    # Set if the card is closed or active
    def set_card_is_closed(self, card):
        pass

    # Set due datetime
    def set_card_due_datetime(self, card):
        pass

    # Remove due datetime
    def remove_card_due_datetime(self, card):
        pass
