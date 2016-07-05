from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.query_utils import Q

from trello import Board as TrelloBoard
from collections import namedtuple

# Task board
class Board(models.Model):
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="boards")
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the board", unique=True)
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)

    def fetch(self):
        self._fetch_labels()
        self._fetch_cards()

    def _fetch_labels(self):
        self.labels.all().delete()
        trello_board = self._get_trello_board()
        trello_labels = trello_board.get_labels()
        for trello_label in trello_labels:
            label = Label.factory_from_trello_label(trello_label, self)
            label.save()

    def _fetch_cards(self):
        self.cards.all().delete()
        trello_board = self._get_trello_board()
        trello_cards = trello_board.all_cards()

        ListForStats = namedtuple('ListForStats', 'id django_id')
        trello_lists = [ListForStats(id=list_.uuid, django_id=list_.id) for list_ in self.lists.all()]
        trello_cycle_dict = {list_.uuid: True for list_ in self.lists.filter(Q(type="done") | Q(type="development"))}
        done_list = self.lists.filter(type="done")[0]
        trello_list_done = ListForStats(id=done_list.uuid, django_id=done_list.id)

        def list_cmp(list_1, list_2):
            if list_1.django_id < list_2.django_id:
                return 1
            if list_1.django_id > list_2.django_id:
                return -1
            return 0

        # Card creation
        for trello_card in trello_cards:
            trello_card.fetch(eager=False)
            card = Card.factory_from_trello_card(trello_card, self)

            # Cycle and Lead times
            if trello_card.idList == done_list.uuid:
                card_stats_by_list = trello_card.get_stats_by_list(lists=trello_lists, list_cmp=list_cmp,
                                                                   done_list=trello_list_done,
                                                                   time_unit="hours", card_movements_filter=None)
                card.lead_time = sum([list_stats["time"] for list_uuid, list_stats in card_stats_by_list.items()])
                card.cycle_time = sum(
                    [list_stats["time"] if list_uuid in trello_cycle_dict else 0 for list_uuid, list_stats in
                     card_stats_by_list.items()])

            card.save()

            # Label assignment to each card
            label_uuids = trello_card.idLabels
            card_labels = self.labels.filter(uuid__in=label_uuids)
            for card_label in card_labels:
                card.labels.add(card_label)

    def _get_trello_board(self):
        trello_client = self.member.trello_client
        trello_board = TrelloBoard(client=trello_client, board_id=self.uuid)
        trello_board.fetch()
        return trello_board


# Card of the task board
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
    cycle_time = models.DecimalField(verbose_name=u"Lead time", decimal_places=4, max_digits=12, default=None, null=True)
    lead_time = models.DecimalField(verbose_name=u"Cycle time", decimal_places=4, max_digits=12, default=None, null=True)
    labels = models.ManyToManyField("boards.Label", related_name="cards")

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cards")
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="cards")

    @staticmethod
    def factory_from_trello_card(trello_card, board):
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


# Label of the task board
class Label(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the label")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the label", unique=True)
    color = models.CharField(max_length=128, verbose_name=u"Color of the label")
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="labels")

    @staticmethod
    def factory_from_trello_label(trello_label, board):
        return Label(uuid=trello_label.id, name=trello_label.name, color=trello_label.color, board=board)

    def avg_estimated_time(self, **kwargs):
        avg_estimated_time = self.cards.filter(**kwargs).aggregate(Avg("estimated_time"))["estimated_time__avg"]
        return avg_estimated_time

    def avg_spent_time(self, **kwargs):
        avg_spent_time = self.cards.filter(**kwargs).aggregate(Avg("spent_time"))["spent_time__avg"]
        return avg_spent_time

    def avg_cycle_time(self, **kwargs):
        avg_cycle_time = self.cards.filter(**kwargs).aggregate(Avg("cycle_time"))["cycle_time__avg"]
        return avg_cycle_time

    def avg_lead_time(self, **kwargs):
        avg_lead_time = self.cards.filter(**kwargs).aggregate(Avg("lead_time"))["lead_time__avg"]
        return avg_lead_time


# List of the task board
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

