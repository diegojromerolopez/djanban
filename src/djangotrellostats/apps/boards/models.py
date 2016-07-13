from __future__ import unicode_literals

import re
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db import models
from django.db.models import Avg
from django.db.models.query_utils import Q
from django.utils import timezone
import copy
import numpy
import datetime
import math
import pytz

from trello import Board as TrelloBoard
from collections import namedtuple
from djangotrellostats.apps.dev_times.models import DailySpentTime


# Abstract model that represents the immutable objects
class ImmutableModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.id is not None:
            raise ValueError(u"This model does not allow edition")
        super(ImmutableModel, self).save(*args, **kwargs)


# Task board
class Board(models.Model):
    creator = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="created_boards")
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the board", unique=True)
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)
    last_fetch_datetime = models.DateTimeField(verbose_name=u"Last fetch datetime", default=None, null=True)

    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="boards")

    def get_human_fetch_datetime(self):
        return self.last_fetch_datetime.strftime("%Y-%m-%d")

    def is_ready(self):
        done_list_exists = self.lists.filter(type="done").exists()
        development_list_exists = self.lists.filter(type="development").exists()
        return done_list_exists and development_list_exists

    def cycle_time_lists(self):
        return self.lists.exclude(Q(type="before_development")|Q(type="ignored"))

    def lead_time_lists(self):
        return self.lists.exclude(Q(type="ignored"))

    # Fetch data of this board
    @transaction.atomic
    def fetch(self):
        self._fetch_labels()
        self._fetch_cards()
        self.last_fetch_datetime = timezone.now()
        self.save()

    # Fetch the labels of this board
    def _fetch_labels(self):
        trello_board = self._get_trello_board()
        trello_labels = trello_board.get_labels()
        for trello_label in trello_labels:
            label = Label.factory_from_trello_label(trello_label, self)
            label.save()

    # Fetch the cards of this board
    def _fetch_cards(self):

        lists = self.lists.all()

        workflows = self.workflows.all()

        trello_cycle_dict = {list_.uuid: True for list_ in self.cycle_time_lists()}
        trello_lead_dict = {list_.uuid: True for list_ in self.lead_time_lists()}
        done_list = lists.get(type="done")

        # List reports
        list_report_dict = {list_.uuid: ListReport(list=list_, forward_movements=0, backward_movements=0)
                            for list_ in lists}

        # Member report
        member_report_dict = {member.uuid: MemberReport(board=self, member=member) for member in
                              self.members.all()}

        # Fetch cards of this board
        trello_board = self._get_trello_board()
        trello_cards = trello_board.all_cards()

        # Card stats computation
        for trello_card in trello_cards:
            trello_card.fetch(eager=False)
            card = Card.factory_from_trello_card(trello_card, self)

            card.get_stats_by_list(lists, done_list)

            # Total forward and backward movements of a card
            card_forward_moves = 0
            card_backward_moves = 0
            card_time = 0

            # List reports. For each list compute the number of forward movements and backward movements
            # being it its the source.
            # Thus, compute the time the cards live in this list.
            for list_ in lists:
                list_uuid = list_.uuid
                card_stats_by_list = card.stats_by_list[list_uuid]

                # Time the card lives in each list
                if not hasattr(list_report_dict[list_uuid], "times"):
                    list_report_dict[list_uuid].times = []

                # Time a card lives in the list
                list_report_dict[list_uuid].times.append(card_stats_by_list["time"])

                # Forward and backward movements where the list is the source
                list_report_dict[list_uuid].forward_movements += card_stats_by_list["forward_moves"]
                list_report_dict[list_uuid].backward_movements += card_stats_by_list["backward_moves"]

                card_time += card_stats_by_list["time"]

                # Update total forward and backward movements
                card_forward_moves += card_stats_by_list["forward_moves"]
                card_backward_moves += card_stats_by_list["backward_moves"]

            # Cycle and Lead times
            if trello_card.idList == done_list.uuid:
                card.lead_time = sum(
                    [list_stats["time"] if list_uuid in trello_lead_dict else 0 for list_uuid, list_stats in
                     card.stats_by_list.items()])

                card.cycle_time = sum(
                    [list_stats["time"] if list_uuid in trello_cycle_dict else 0 for list_uuid, list_stats in
                     card.stats_by_list.items()])

            card.save()

            # Label assignment to each card
            label_uuids = trello_card.idLabels
            card_labels = self.labels.filter(uuid__in=label_uuids)
            for card_label in card_labels:
                card.labels.add(card_label)

            # Member reports
            trello_card_member_uuids = card.member_uuids
            num_trello_card_members = len(trello_card_member_uuids)
            for trello_member_uuid in trello_card_member_uuids:
                member_report = member_report_dict[trello_member_uuid]

                # Increment the number of cards of the member report
                member_report.number_of_cards += 1

                # Forward movements of the cards
                if member_report.forward_movements is None:
                    member_report.forward_movements = 0
                member_report.forward_movements += math.ceil(1. * card_forward_moves / 1. * num_trello_card_members)

                # Backward movements of the cards
                if member_report.backward_movements is None:
                    member_report.backward_movements = 0
                member_report.backward_movements += math.ceil(1. * card_backward_moves / 1. * num_trello_card_members)

                # Inform this member report has data and must be saved
                member_report.present = True

                # Card time
                if not hasattr(member_report, "card_times"):
                    member_report.card_times = []
                if card_time is not None:
                    member_report.card_times.append(card_time)

                # Card spent time
                if not hasattr(member_report, "card_spent_times"):
                    member_report.card_spent_times = []
                if card.spent_time_by_member.get(trello_member_uuid) is not None:
                    member_report.card_spent_times.append(card.spent_time_by_member.get(trello_member_uuid))

                # Card estimated time
                if not hasattr(member_report, "card_estimated_times"):
                    member_report.card_estimated_times = []
                if card.estimated_time_by_member.get(trello_member_uuid) is not None:
                    member_report.card_estimated_times.append(card.estimated_time_by_member.get(trello_member_uuid))

                # Workflow card reports
                for workflow in workflows:
                    workflow.fetch([card])

        # Average and std. deviation of time cards live in this list
        for list_uuid, list_report in list_report_dict.items():
            if hasattr(list_report, "times"):
                list_report.avg_card_time = numpy.mean(list_report.times)
                list_report.std_dev_card_time = numpy.std(list_report.times, axis=0)
            list_report.save()

        # Average and std. deviation of card times by member
        for member_uuid, member_report in member_report_dict.items():
            if hasattr(member_report, "present") and member_report.present:
                # Average and std deviation of the time of member cards
                if len(member_report.card_times) > 0:
                    member_report.avg_card_time = numpy.mean(member_report.card_times)
                    member_report.std_dev_card_time = numpy.std(member_report.card_times)

                # Average and std deviation of the spent time of member cards
                if len(member_report.card_spent_times) > 0:
                    member_report.avg_card_spent_time = numpy.mean(member_report.card_spent_times)
                    member_report.std_dev_card_spent_time = numpy.std(member_report.card_spent_times)

                # Average and std deviation of the estimated time of member cards
                if len(member_report.card_estimated_times) > 0:
                    member_report.avg_card_estimated_time = numpy.mean(member_report.card_estimated_times)
                    member_report.std_dev_card_estimated_time = numpy.std(member_report.card_estimated_times)

                member_report.save()

    # Return the trello board, calling the Trello API.
    def _get_trello_board(self):
        trello_client = self.creator.trello_client
        trello_board = TrelloBoard(client=trello_client, board_id=self.uuid)
        trello_board.fetch()
        return trello_board


# Card of the task board
class Card(ImmutableModel):
    COMMENT_SPENT_ESTIMATED_TIME_REGEX = r"^plus!\s(?P<spent>(\-)?\d+(\.\d+)?)/(?P<estimated>(\-)?\d+(\.\d+)?)"

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cards")
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="cards")

    name = models.TextField(verbose_name=u"Name of the card")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the card", unique=True)
    url = models.CharField(max_length=512, verbose_name=u"URL of the card")
    short_url = models.CharField(max_length=128, verbose_name=u"Short URL of the card")
    description = models.TextField(verbose_name=u"Description of the card")
    is_closed = models.BooleanField(verbose_name=u"Is this card closed?", default=False)
    position = models.PositiveIntegerField(verbose_name=u"Position in the list")
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date")
    spent_time = models.DecimalField(verbose_name=u"Actual card spent time", decimal_places=4, max_digits=12,
                                     default=None, null=True)
    estimated_time = models.DecimalField(verbose_name=u"Estimated card completion time", decimal_places=4,
                                         max_digits=12, default=None, null=True)
    cycle_time = models.DecimalField(verbose_name=u"Lead time", decimal_places=4, max_digits=12, default=None,
                                     null=True)
    lead_time = models.DecimalField(verbose_name=u"Cycle time", decimal_places=4, max_digits=12, default=None,
                                    null=True)
    labels = models.ManyToManyField("boards.Label", related_name="cards")

    @staticmethod
    def factory_from_trello_card(trello_card, board):
        list_ = board.lists.get(uuid=trello_card.idList)

        card = Card(uuid=trello_card.id, name=trello_card.name, url=trello_card.url,
                    short_url=trello_card.short_url, description=trello_card.desc, is_closed=trello_card.closed,
                    position=trello_card.pos, last_activity_date=trello_card.dateLastActivity,
                    board=board, list=list_
                    )

        # Store the trello card data for ease of use
        card.trello_card = trello_card

        # Card comments
        comment_summary = card.fetch_comments()

        # Card spent and estimated times
        card.spent_time = comment_summary["spent"]["total"]
        card.estimated_time = comment_summary["estimated"]["total"]

        # Dynamic attributes

        # Spent and estimated time by member
        card.spent_time_by_member = comment_summary["spent"]["by_member"]
        card.estimated_time_by_member = comment_summary["estimated"]["by_member"]

        # Members that play a role in this task
        card_member_uuids = {member_uuid: True for member_uuid in trello_card.idMembers}
        card_member_uuids.update({member_uuid: True for member_uuid in comment_summary["member_uuids"]})
        card.member_uuids = card_member_uuids.keys()

        return card

    # Compute the stats of this card
    def get_stats_by_list(self, lists, done_list):
        # Use cache to avoid recomputing this stats
        if hasattr(self, "stats_by_list"):
            return self.stats_by_list

        # trello_card attribute of the Card object is needed to compute the stats
        if not hasattr(self, "trello_card"):
            raise ValueError(u"Something is wrong. Not 'trello_card' attribute found. Did you create the card without "
                             u"calling Card.factory_from_trello_card?")

        # Fake class used for passing a list of trello lists to the method of Card stats_by_list
        ListForStats = namedtuple('ListForStats', 'id django_id')
        fake_trello_lists = [ListForStats(id=list_.uuid, django_id=list_.id) for list_ in lists]
        fake_trello_list_done = ListForStats(id=done_list.uuid, django_id=done_list.id)

        # Hash to obtain the order of a list given its uuid
        trello_list_order_dict = {list_.uuid: list_.id for list_ in lists}

        # Comparator function
        def list_cmp(list_1, list_2):
            list_1_order = trello_list_order_dict[list_1]
            list_2_order = trello_list_order_dict[list_2]
            if list_1_order < list_2_order:
                return 1
            if list_1_order > list_2_order:
                return -1
            return 0

        self.lists = lists
        self.done_list = done_list
        self.stats_by_list = self.trello_card.get_stats_by_list(lists=fake_trello_lists,
                                                                list_cmp=list_cmp,
                                                                done_list=fake_trello_list_done,
                                                                time_unit="hours", card_movements_filter=None)

        return self.stats_by_list

    def fetch_comments(self):
        trello_card_comments = self.trello_card.fetch_comments()
        self.comments = trello_card_comments

        total_spent = None
        total_estimated = None
        spent_by_member = {}
        estimated_by_member = {}
        member_uuids = {}

        # Comment format:
        # {u'type': u'commentCard', u'idMemberCreator': u'56e2ac8e14e4eda06ac6b8fd',
        #  u'memberCreator': {u'username': u'diegoj5', u'fullName': u'Diego J.', u'initials': u'DJ',
        #                     u'id': u'56e2ac8e14e4eda06ac6b8fd', u'avatarHash': u'a3086f12908905354b15972cd67b64f8'},
        #  u'date': u'2016-04-20T23:06:38.279Z',
        #  u'data': {u'text': u'Un comentario', u'list': {u'name': u'En desarrollo', u'id': u'5717fb3fde6bdaed40201667'},
        #            u'board': {u'id': u'5717fb368199521a139712f0', u'name': u'Test', u'shortLink': u'2CGPEnM2'},
        #            u'card': {u'idShort': 6, u'id': u'57180ae1ed24b1cff7f8da7c', u'name': u'Por todas',
        #                      u'shortLink': u'bnK3c1jF'}}, u'id': u'57180b7e25abc60313461aaf'}

        # For each comment, find the desired pattern and extract the spent and estimated times
        for comment in self.comments:
            comment_content = comment["data"]["text"]
            matches = re.match(Card.COMMENT_SPENT_ESTIMATED_TIME_REGEX, comment_content)
            if matches:
                # Member uuid that has made this Plus for Trello Comment
                member_uuid = comment["idMemberCreator"]
                member_uuids[member_uuid] = True

                # Spent time when developing this task
                spent = float(matches.group("spent"))

                # Add to spent by member
                if member_uuid not in spent_by_member:
                    spent_by_member[member_uuid] = 0
                spent_by_member[member_uuid] += spent

                # Add to total spent
                if total_spent is None:
                    total_spent = 0

                total_spent += spent

                # Estimated time for developing this task
                estimated = float(matches.group("estimated"))

                # Add to estimated by member
                if member_uuid not in estimated_by_member:
                    estimated_by_member[member_uuid] = 0
                estimated_by_member[member_uuid] += estimated

                # Add to total estimated
                if total_estimated is None:
                    total_estimated = 0

                total_estimated += estimated

                # Store spent time by member by day
                local_timezone = pytz.timezone(settings.TIME_ZONE)
                comment_date = local_timezone.localize(datetime.datetime.strptime(comment["date"],
                                                                                  '%Y-%m-%dT%H:%M:%S.%fZ')).date()

                DailySpentTime.add(board=self.board, member=member_uuid, date=comment_date,
                                   spent_time=spent, estimated_time=estimated)

        self.comment_summary = {
            "member_uuids": member_uuids.keys(),
            "spent": {"total": total_spent, "by_member": spent_by_member},
            "estimated": {"total": total_estimated, "by_member": estimated_by_member}
        }
        return self.comment_summary


# Label of the task board
class Label(ImmutableModel):

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
    LIST_TYPES = ("ignored", "before_development", "development", "after_development", "done", "closed")
    LIST_TYPE_CHOICES = (
        ("ignored", "Ignored"),
        ("before_development", "Before development"),
        ("development", "In development"),
        ("after_development", "After development"),
        ("done", "Done"),
        ("closed", "Closed"),
    )
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the list", unique=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="lists")
    type = models.CharField(max_length=64, choices=LIST_TYPE_CHOICES, default="before_development")


# Stat report by list
class ListReport(models.Model):
    list = models.OneToOneField("boards.List", verbose_name=u"List", related_name="list_reports", unique=True)
    forward_movements = models.PositiveIntegerField(verbose_name=u"Forward movements")
    backward_movements = models.PositiveIntegerField(verbose_name=u"Backward movements")
    avg_card_time = models.DecimalField(verbose_name=u"Average time cards live in this list", decimal_places=4,
                                        max_digits=12, default=None, null=True)
    std_dev_card_time = models.DecimalField(verbose_name=u"Average time cards live in this list", decimal_places=4,
                                            max_digits=12, default=None, null=True)


# Stat report by member
class MemberReport(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="member_reports")
    number_of_cards = models.PositiveIntegerField(verbose_name=u"Number of assigned cards", default=0)
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="member_reports")
    forward_movements = models.PositiveIntegerField(verbose_name=u"Forward movements")
    backward_movements = models.PositiveIntegerField(verbose_name=u"Backward movements")
    avg_card_time = models.DecimalField(verbose_name=u"Average time a card lives in the board", decimal_places=4,
                                        max_digits=12, default=None, null=True)
    std_dev_card_time = models.DecimalField(verbose_name=u"Std. Dev. time a card lives in the board", decimal_places=4,
                                            max_digits=12, default=None, null=True)
    avg_card_spent_time = models.DecimalField(verbose_name=u"Average card spent time", decimal_places=4, max_digits=12,
                                              default=None, null=True)
    std_dev_card_spent_time = models.DecimalField(verbose_name=u"Std. Deviation card spent time", decimal_places=4,
                                                  max_digits=12,
                                                  default=None, null=True)
    avg_card_estimated_time = models.DecimalField(verbose_name=u"Average task estimated card completion time",
                                                  decimal_places=4,
                                                  max_digits=12, default=None, null=True)
    std_dev_card_estimated_time = models.DecimalField(verbose_name=u"Std. Deviation of the estimated card completion time",
                                                 decimal_places=4,
                                                 max_digits=12, default=None, null=True)


# Stat report by workflow
class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the workflow")
    board = models.ForeignKey("boards.Board", verbose_name=u"Workflow", related_name="workflows")
    lists = models.ManyToManyField("boards.List", through="WorkflowList", related_name="workflow")

    # Fetch data for this workflow, creating a workflow report
    def fetch(self, cards):
        workflow_lists = self.workflow_lists.all()
        development_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                             self.workflow_lists.filter(is_done_list=False)}
        done_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                      self.workflow_lists.filter(is_done_list=True)}

        workflow_card_reports = []

        for card in cards:
            trello_card = card.trello_card

            lead_time = None
            cycle_time = None

            # Lead time and cycle time only should be computed when the card is done
            if not card.is_closed and trello_card.idList in done_lists:
                # Lead time in this workflow for this card
                lead_time = sum([list_stats["time"] for list_uuid, list_stats in card.stats_by_list.items()])

                # Cycle time in this workflow for this card
                cycle_time = sum(
                    [list_stats["time"] if list_uuid in development_lists else 0 for list_uuid, list_stats in
                     card.stats_by_list.items()])

                workflow_card_report = WorkflowCardReport(board=self.board, workflow=self,
                                                          card=card, cycle_time=cycle_time, lead_time=lead_time)
                workflow_card_report.save()

                workflow_card_reports.append(workflow_card_report)

        return workflow_card_reports


class WorkflowList(models.Model):
    order = models.PositiveIntegerField(verbose_name=u"Order of the list")
    is_done_list = models.BooleanField(verbose_name=u"Informs if the list is a done list", default=False)
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="workflow_list")
    workflow = models.ForeignKey("boards.Workflow", verbose_name=u"Workflow", related_name="workflow_lists")


class WorkflowCardReport(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="workflow_card_reports")
    workflow = models.ForeignKey("boards.Workflow", verbose_name=u"Workflow", related_name="workflow_card_reports")
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="workflow_card_reports")
    lead_time = models.DecimalField(verbose_name=u"Card cycle card time", decimal_places=4,
                                    max_digits=12, default=None, null=True)
    cycle_time = models.DecimalField(verbose_name=u"Card lead time", decimal_places=4, max_digits=12,
                                     default=None,
                                     null=True)


