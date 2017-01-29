# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djangotrellostats.trello_api.connector import TrelloConnector
from trello import Card as TrelloCard
from trello import List as TrelloList


# Return the trello board of a given Board object.
def get_trello_board(board, member):
    trello_connector = TrelloConnector(member)
    trello_board = trello_connector.trello_client.get_board(board.uuid)
    return trello_board


# Return a trello list
def get_trello_list(list_, member):
    trello_board = get_trello_board(list_.board, member)
    trello_list = TrelloList(trello_board, list_.uuid, name=list_.name)
    return trello_list


# Return the trello card of a given Card object.
# The member is used to establish the connection.
def get_trello_card(card, member):
    trello_board = get_trello_board(card.board, member)
    trello_card = TrelloCard(parent=trello_board, card_id=card.uuid)
    return trello_card