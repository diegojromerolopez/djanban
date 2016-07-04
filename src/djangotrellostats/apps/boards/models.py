from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.db import models

from trello import Board as TrelloBoard


class Board(models.Model):
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="boards")
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the board", unique=True)
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)

    def fetch_labels(self):
        trello_board = self._get_trello_board()

    def fetch_cards(self):
        trello_board = self._get_trello_board()
        trello_cards = trello_board.all_cards()
        for trello_card in trello_cards:
            trello_card.fetch(eager=False)
            card = Card.factory_from_trello_card(trello_card)
            card.save()

    def _get_trello_board(self):
        trello_client = self.member.trello_client
        trello_board = TrelloBoard(client=trello_client, board_id=self.uuid)
        trello_board.fetch()
        return trello_board


class Card(models.Model):
    COMMENT_SPENT_ESTIMATED_TIME_REGEX = r"^plus!\s(?P<spent>(\-)?\d+(\.\d+)?)/(?P<estimated>(\-)?\d+(\.\d+)?)"
    name = models.CharField(max_length=128, verbose_name=u"Name of the card")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the card", unique=True)
    url = models.CharField(max_length=128, verbose_name=u"URL of the card")
    short_url = models.CharField(max_length=128, verbose_name=u"Short URL of the card")
    description = models.TextField(verbose_name=u"Description of the card")
    is_closed = models.BooleanField(verbose_name=u"Is this card closed?", default=False)
    position = models.PositiveIntegerField(verbose_name=u"Position in the list")
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date")
    spent_time = models.DecimalField(verbose_name=u"Actual card spent time", decimal_places=4, max_digits=12, default=None, null=True)
    estimated_time = models.DecimalField(verbose_name=u"Estimated card completion time", decimal_places=4, max_digits=12, default=None, null=True)

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cards")
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="cards")

    @staticmethod
    def factory_from_trello_card(trello_card):
        board = Board.objects.get(uuid=trello_card.idBoard)
        list_ = board.lists.get(uuid=trello_card.idList)
        card = Card(uuid=trello_card.id, name=trello_card.name, url=trello_card.url, short_url=trello_card.short_url,
                    description=trello_card.desc, is_closed=trello_card.closed, position=trello_card.pos,
                    last_activity_date=trello_card.dateLastActivity,
                    board=board, list=list_
                )
        # Card spent and estimated times
        trello_card_comments = trello_card.fetch_comments()
        card_times = Card._get_times_from_trello_comments(trello_card_comments)
        card.spent_time = card_times["spent"]
        card.estimated_time = card_times["estimated"]
        return card

    @staticmethod
    def _get_times_from_trello_comments(comments):
        total_spent = None
        total_estimated = None
        # For each comment, find the desired pattern and extract the spent and estimated times
        for comment in comments:
            comment_content = comment["data"]["text"]
            matches = re.match(Card.COMMENT_SPENT_ESTIMATED_TIME_REGEX, comment_content)
            if matches:
                # Add to total spent
                if total_spent is None:
                    total_spent = 0
                spent = float(matches.group("spent"))
                total_spent += spent
                # Add to total estimated
                if total_estimated is None:
                    total_estimated = 0
                estimated = float(matches.group("estimated"))
                total_estimated += estimated

        return {"estimated": total_estimated, "spent": total_spent}


class Label(object):
    pass


class List(models.Model):
    LIST_TYPES = ("normal", "development", "done")
    LIST_TYPE_CHOICES = (
        ("normal", "Normal"),
        ("development", "In development"),
        ("done", "Done")
    )
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the list", unique=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="lists")
    type = models.CharField(max_length=64, choices=LIST_TYPE_CHOICES, default="normal")





class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the workflow")
    board = models.ForeignKey("boards.Board", verbose_name=u"Workflow", related_name="workflows")
    lists = models.ManyToManyField("boards.List", through="WorkflowList", related_name="workflow")


class WorkflowList(models.Model):
    order = models.PositiveIntegerField(verbose_name=u"Order of the list")
    is_done_list = models.BooleanField(verbose_name=u"Informs if the list is a done list", default=False)
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="workflowlist")
    workflow = models.ForeignKey("boards.Workflow", verbose_name=u"Workflow", related_name="workflowlists")

