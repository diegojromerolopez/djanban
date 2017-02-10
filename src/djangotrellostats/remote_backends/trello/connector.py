# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple

from django.utils import timezone
from trello import TrelloClient
from trello import Card as TrelloCard
from trello import List as TrelloList


# Establishes a connection with Trello API
class TrelloConnector(object):

    def __init__(self, member):
        self.member = member
        self.trello_member_profile = member.trello_member_profile
        self.trello_client = self._get_trello_client()

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.trello_member_profile.api_key,
            api_secret=self.trello_member_profile.api_secret,
            token=self.trello_member_profile.token,
            token_secret=self.trello_member_profile.token_secret
        )
        return client

    def reconnect(self):
        self.trello_client = self._get_trello_client()

    # Return the trello board of a given Board object.
    def get_trello_board(self, board):
        trello_board = self.trello_client.get_board(board.uuid)
        return trello_board

    # Return a trello list
    def get_trello_list(self, list_):
        trello_board = self.get_trello_board(list_.board)
        trello_list = TrelloList(trello_board, list_.uuid, name=list_.name)
        return trello_list

    # Return the trello card of a given Card object.
    # The member is used to establish the connection.
    def get_trello_card(self, card):
        trello_board = self.get_trello_board(card.board)
        trello_card = TrelloCard(parent=trello_board, card_id=card.uuid)
        return trello_card

    # Member operations

    # Add existing member to this board
    def add_member(self, board, member_to_add, member_type="normal"):
        # Getting trello board
        trello_board = self.get_trello_board(board)
        FakeTrelloMember = namedtuple("FakeTrelloMember", ["id"])
        fake_trello_member_to_add = FakeTrelloMember(id=member_to_add.uuid)
        return trello_board.add_member(fake_trello_member_to_add, member_type)

    # Delete member from this board
    def remove_member(self, board, member_to_remove):
        # Getting trello board
        trello_board = self.get_trello_board(board)
        FakeTrelloMember = namedtuple("FakeTrelloMember", ["id"])
        fake_trello_member_to_remove = FakeTrelloMember(id=member_to_remove.uuid)
        return trello_board.remove_member(fake_trello_member_to_remove)

    # List operations

    # Move list list_ to the position
    # member is used for authentication
    def move_list(self, list_, position):
        trello_list = self.get_trello_list(list_)
        return trello_list.move(position)

    # Create a new list
    def new_list(self, new_list):
        trello_board = self.get_trello_board(new_list.board)
        trello_list = trello_board.add_list(new_list.name, pos=new_list.position)
        new_list.uuid = trello_list.id
        new_list.creation_datetime = timezone.now()
        new_list.last_activity_datetime = timezone.now()
        return new_list

    # Card operations

    # Creates a new card
    def new_card(self, card, labels=None, position="bottom"):

        # Getting trello board
        trello_board = self.get_trello_board(card.board)
        trello_list = trello_board.get_list(list_id=card.list.uuid)

        # PyTrello API needs the labels to be to be an object with a label id, so we construct a
        # fake object with a label id inside
        trello_labels = []
        if labels:
            TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
            trello_labels = [TrelloLabelUuid(id=label.uuid) for label in labels]

        # Calling the Trello API to create the card
        trello_card = trello_list.add_card(
            card.name, desc=card.description,
            labels=trello_labels, due="null",
            source=None, position=position
        )

        # Card attribute assignment
        card.uuid = trello_card.id
        card.short_url = trello_card.shortUrl
        card.url = trello_card.url
        card.position = trello_card.pos
        card.creation_datetime = timezone.now()
        card.last_activity_datetime = timezone.now()
        return card

    # Order card
    def order_card(self, card, position):
        trello_card = self.get_trello_card(card)
        return trello_card.change_pos(position)

    # Move the card to other list
    def move_card(self, card, destination_list):
        trello_card = self.get_trello_card(card)
        return trello_card.change_list(destination_list.uuid)

    # Move all cards from a list
    def move_list_cards(self, source_list, destination_list):
        trello_list = self.get_trello_list(source_list)
        # FakeTrelloBoard and FakeTrelloList are needed because the pytrello API needs an
        # object (list) with an id and a board (also with an id)
        # There is no easy way to do it, unless you want to construct a TrelloBoard or fetch a TrelloBoard
        FakeTrelloBoard = namedtuple("FakeTrelloBoard", ["id"])
        fake_trello_board = FakeTrelloBoard(id=source_list.board.uuid)
        FakeTrelloList = namedtuple("FakeTrelloList", ["id", "board"])
        fake_trello_destination_list = FakeTrelloList(id=destination_list.uuid, board=fake_trello_board)
        return trello_list.move_all_cards(fake_trello_destination_list)

    # Add comment to a card
    def add_comment_to_card(self, card, comment):
        trello_card = self.get_trello_card(card)
        trello_comment = trello_card.comment(comment.content)
        comment.uuid = trello_comment["id"]
        comment.last_edition_datetime = None
        return comment

    # Edit comment content
    def edit_comment_of_card(self, card, comment):
        if self.member.uuid != comment.author.uuid:
            raise AssertionError(u"You can only edit your comments")
        trello_card = self.get_trello_card(card)
        trello_card.update_comment(comment.uuid, comment.content)
        comment.last_edition_datetime = timezone.now()
        return comment

    # Delete comment of card
    def delete_comment_of_card(self, card, comment):
        trello_card = self.get_trello_card(card)
        return trello_card.delete_comment({"id": comment.uuid})

    # Add a labels to a card
    def add_label_to_card(self, card, label):
        trello_card = self.get_trello_card(card)
        TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
        return trello_card.add_label(TrelloLabelUuid(id=label.uuid))

    # Add a labels to a card
    def remove_label_of_card(self, card, label):
        trello_card = self.get_trello_card(card)
        TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
        return trello_card.remove_label(TrelloLabelUuid(id=label.uuid))

    # Sets the name of the card in Trello
    def set_card_name(self, card):
        trello_card = self.get_trello_card(card)
        return trello_card.set_name(card.name)

    # Sets the description of the card in Trello
    def set_card_description(self, card):
        trello_card = self.get_trello_card(card)
        return trello_card.set_description(card.description)

    # Set if the card is closed or active
    def set_card_is_closed(self, card):
        trello_card = self.get_trello_card(card)
        return trello_card.set_closed(card.is_closed)

    # Set due datetime
    def set_card_due_datetime(self, card):
        trello_card = self.get_trello_card(card)
        return trello_card.set_due(card.due_datetime)

    # Remove due datetime
    def remove_card_due_datetime(self, card):
        trello_card = self.get_trello_card(card)
        return trello_card.remove_due()
