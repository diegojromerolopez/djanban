# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djangotrellostats.trello_api.common import get_trello_board, get_trello_list
from djangotrellostats.trello_api.connector import TrelloConnector
from trello import Card as TrelloCard
from trello import List as TrelloList
from collections import namedtuple

def move_list(list_, member, position):
    trello_list = get_trello_list(list_, member)
    return trello_list.move(position)

