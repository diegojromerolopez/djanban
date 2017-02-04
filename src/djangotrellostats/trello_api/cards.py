# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djangotrellostats.trello_api.common import get_trello_board, get_trello_card, get_trello_list
from djangotrellostats.trello_api.connector import TrelloConnector
from trello import Card as TrelloCard
from trello import List as TrelloList
from collections import namedtuple


# Creates a new card
def new_card(card, member=None, labels=None, position="bottom"):

    # We can pass the member through the card
    if member is None:
        member = card.member

    # Getting trello board
    trello_board = get_trello_board(card.board, member)
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
    return trello_card


# Order card
def order_card(card, member, position):
    trello_card = get_trello_card(card, member)
    trello_card.change_pos(position)


# Move the card to other list
def move_card(card, member, destination_list):
    trello_card = get_trello_card(card, member)
    trello_card.change_list(destination_list.uuid)


# Move all cards from a list
def move_list_cards(source_list, member, destination_list):
    trello_list = get_trello_list(source_list, member)
    # FakeTrelloBoard and FakeTrelloList are needed because the pytrello API needs an
    # object (list) with an id and a board (also with an id)
    # There is no easy way to do it, unless you want to construct a TrelloBoard or fetch a TrelloBoard
    FakeTrelloBoard = namedtuple("FakeTrelloBoard", ["id"])
    fake_trello_board = FakeTrelloBoard(id=source_list.board.uuid)
    FakeTrelloList = namedtuple("FakeTrelloList", ["id", "board"])
    fake_trello_destination_list = FakeTrelloList(id=destination_list.uuid, board=fake_trello_board)
    trello_list.move_all_cards(fake_trello_destination_list)


# Add comment to a card
def add_comment_to_card(card, member, content):
    trello_card = get_trello_card(card, member)
    return trello_card.comment(content)


# Edit comment content
def edit_comment_of_card(card, member, comment, new_content):
    if member.uuid != comment.author.uuid:
        raise AssertionError(u"You can only edit your comments")
    trello_card = get_trello_card(card, member)
    return trello_card.update_comment(comment.uuid, new_content)


# Delete comment of card
def delete_comment_of_card(card, member, comment):
    trello_card = get_trello_card(card, member)
    return trello_card.delete_comment({"id": comment.uuid})


# Add a labels to a card
def add_label_to_card(card, member, label):
    trello_card = get_trello_card(card, member)
    TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
    return trello_card.add_label(TrelloLabelUuid(id=label.uuid))


# Add a labels to a card
def remove_label_of_card(card, member, label):
    trello_card = get_trello_card(card, member)
    TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
    return trello_card.remove_label(TrelloLabelUuid(id=label.uuid))


# Sets the name of the card in Trello
def set_name(card, member):
    trello_card = get_trello_card(card, member)
    return trello_card.set_name(card.name)


# Sets the description of the card in Trello
def set_description(card, member):
    trello_card = get_trello_card(card, member)
    return trello_card.set_description(card.description)


# Set if the card is closed or active
def set_is_closed(card, member):
    trello_card = get_trello_card(card, member)
    return trello_card.set_closed(card.is_closed)