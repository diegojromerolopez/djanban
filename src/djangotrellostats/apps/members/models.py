# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from trello import TrelloClient

from djangotrellostats.apps.boards.models import Board, List


class Member(models.Model):
    api_key = models.CharField(max_length=128, verbose_name=u"Trello API key")
    api_secret = models.CharField(max_length=128, verbose_name=u"Trello API secret")
    token = models.CharField(max_length=128, verbose_name=u"Trello token")
    token_secret = models.CharField(max_length=128, verbose_name=u"Trello token secret")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello member uuid")
    trello_username = models.CharField(max_length=128, verbose_name=u"Trello username")
    initials = models.CharField(max_length=8, verbose_name=u"User initials in Trello")
    user = models.OneToOneField(User, verbose_name=u"Associated user", related_name="member")

    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)

        self.trello_client = self._get_trello_client()

    # Fetch basic information of boards and its lists
    def init_fetch(self):
        self.boards.all().delete()
        trello_boards = self.trello_client.list_boards()
        for trello_board in trello_boards:
            board_name = trello_board.name.decode("utf-8")
            board = Board(uuid=trello_board.id, name=board_name, last_activity_date=trello_board.date_last_activity, member=self)
            board.save()

            # Fetch all lists of this board
            trello_lists = trello_board.all_lists()
            for trello_list in trello_lists:
                list_name = trello_list.name.decode("utf-8")
                _list = List(uuid=trello_list.id, name=list_name, board=board)
                _list.save()

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.api_key,
            api_secret=self.api_secret,
            token=self.token,
            token_secret=self.token_secret
        )
        return client