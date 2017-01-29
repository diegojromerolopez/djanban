# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from djangotrellostats.trello_api.common import get_trello_board


# Add existing member to this board
def add_member(board, current_member, member_to_add, member_type="normal"):
    # Getting trello board
    trello_board = get_trello_board(board, current_member)
    FakeTrelloMember = namedtuple("FakeTrelloMember", ["id"])
    fake_trello_member_to_add = FakeTrelloMember(id=member_to_add.uuid)
    trello_board.add_member(fake_trello_member_to_add, member_type)


# Delete member from this board
def remove_member(board, current_member, member_to_remove):
    # Getting trello board
    trello_board = get_trello_board(board, current_member)
    FakeTrelloMember = namedtuple("FakeTrelloMember", ["id"])
    fake_trello_member_to_remove = FakeTrelloMember(id=member_to_remove.uuid)
    trello_board.remove_member(fake_trello_member_to_remove)

