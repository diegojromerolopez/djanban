# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple

from django.urls import reverse
from django.utils import timezone

from djangotrellostats.utils.custom_uuid import custom_uuid


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
        new_list.creation_datetime = timezone.now()
        new_list.last_activity_datetime = timezone.now()
        return new_list

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
