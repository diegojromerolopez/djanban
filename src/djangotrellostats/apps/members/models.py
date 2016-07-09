# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from trello import TrelloClient

from djangotrellostats.apps.boards.models import Board, List


class Member(models.Model):
    api_key = models.CharField(max_length=128, verbose_name=u"Trello API key", null=True, default=None)
    api_secret = models.CharField(max_length=128, verbose_name=u"Trello API secret", null=True, default=None)
    token = models.CharField(max_length=128, verbose_name=u"Trello token", null=True, default=None)
    token_secret = models.CharField(max_length=128, verbose_name=u"Trello token secret", null=True, default=None)
    uuid = models.CharField(max_length=128, verbose_name=u"Trello member uuid", unique=True)
    trello_username = models.CharField(max_length=128, verbose_name=u"Trello username")
    initials = models.CharField(max_length=8, verbose_name=u"User initials in Trello")
    user = models.OneToOneField(User, verbose_name=u"Associated user", related_name="member", null=True, default=None)

    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)
        self.trello_client = self._get_trello_client()

    # Fetch basic information of boards and its lists
    def init_fetch(self):
        self.boards.all().delete()
        trello_boards = self.trello_client.list_boards()
        for trello_board in trello_boards:
            board_name = trello_board.name.decode("utf-8")
            board = Board(uuid=trello_board.id, name=board_name, last_activity_date=trello_board.date_last_activity, creator=self)
            board.save()

            # Fetch all lists of this board
            trello_lists = trello_board.all_lists()
            for trello_list in trello_lists:
                list_name = trello_list.name.decode("utf-8")
                _list = List(uuid=trello_list.id, name=list_name, board=board)
                _list.save()

            # Fetch all members this board
            self._fetch_members(board, trello_board)

    # Fetch members of this board
    def _fetch_members(self, board, trello_board):
        trello_members = trello_board.all_members()
        for trello_member in trello_members:
            # If the member does not exist, create it with empty Trello credentials
            try:
                member = Member.objects.get(uuid=trello_member.id)
            except Member.DoesNotExist:
                member = Member(uuid=trello_member.id, trello_username=trello_member.username,
                                initials=trello_member.initials)
                member.save()
            # Only add the board to the member if he/she has not it yet
            if not member.boards.filter(uuid=board.uuid).exists():
                member.boards.add(board)

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            token=self.token,
            token_secret=self.token_secret
        )
        return client