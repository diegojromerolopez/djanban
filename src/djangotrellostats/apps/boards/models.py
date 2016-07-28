from __future__ import unicode_literals

import math
import re
import threading
from collections import namedtuple
from datetime import datetime
from datetime import timedelta

import numpy
import pytz
from django.conf import settings
from django.db import models
from django.db import transaction
from django.db.models import Avg, Sum
from django.db.models.query_utils import Q
from django.utils import timezone
from isoweek import Week
from trello import ResourceUnavailable
from trello.board import Board as TrelloBoard

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
    comments = models.TextField(max_length=128, verbose_name=u"Comments for this board", default="", blank=True)
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the board", unique=True)
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)
    last_fetch_datetime = models.DateTimeField(verbose_name=u"Last fetch datetime", default=None, null=True)

    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="boards")
    hourly_rates = models.ManyToManyField("hourly_rates.HourlyRate", verbose_name=u"Hourly rates",
                                          related_name="boards")

    # Returns the date of the last fetch in an ISO format
    def get_human_fetch_datetime(self):
        return self.last_fetch_datetime.strftime("%Y-%m-%d")

    # Returns an hourly rate or None if this doesn't exist
    def get_date_hourly_rate(self, date):
        # Get all hourly rates
        hourly_rates = self.hourly_rates.all()

        # IF there are no hourly rates, return None
        if hourly_rates.count() == 0:
            return None

        for hourly_rate in hourly_rates:
            # If date is inside the interval defined by the dates of the hourly rate
            # this hourly rate will be applied in this day
            if hourly_rate.end_date and hourly_rate.start_date <= date <= hourly_rate.end_date or date >= hourly_rate.start_date:
                return hourly_rate

        return None

    def is_ready(self):
        """
        Informs if this board is ready to be fetched.
        Returns: True if this board's data can be fetched.

        """
        done_list_exists = self.lists.filter(type="done").exists()
        development_list_exists = self.lists.filter(type="development").exists()
        return done_list_exists and development_list_exists

    def is_fetched(self):
        """
        Inform if this board has fetched data.
        Returns: True if the board has data (cards, times...). False otherwise.

        """
        return self.last_fetch_datetime is not None

    def cycle_time_lists(self):
        return self.lists.exclude(Q(type="before_development")|Q(type="ignored"))

    def lead_time_lists(self):
        return self.lists.exclude(Q(type="ignored"))

    # Returns the spent time today for this board
    def get_today_spent_time(self):
        now = timezone.now()
        today = now.date()
        return self.get_spent_time(date=today)

    # Returns the spent time on a given date for this board
    def get_spent_time(self, date):
        spent_time = self.daily_spent_times.filter(date=date).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Return the spent time on a given week of a year
    def get_weekly_spent_time(self, week, year):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Return the spent time on a given month of a year
    def get_monthly_spent_time(self, month, year):
        spent_time_on_week_filter = {"date__month": month, "date__year": year}
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Fetch data of this board
    def fetch(self, debug=False):
        self.trello_board = self._get_trello_board()
        cards = self._fetch_cards(debug=debug)
        with transaction.atomic():
            self._truncate()
            self._fetch_labels()
            self._create_cards(cards)
            self.last_fetch_datetime = timezone.now()
            self.save()

    # Delete all children entities but lists and workflows
    def _truncate(self):
        self.labels.all().delete()
        self.cards.all().delete()
        self.daily_spent_times.all().delete()
        ListReport.objects.filter(list__board=self).delete()
        self.member_reports.all().delete()

    # Fetch the labels of this board
    def _fetch_labels(self):
        trello_labels = self.trello_board.get_labels()
        for trello_label in trello_labels:
            label = Label.factory_from_trello_label(trello_label, self)
            label.save()

    # Return the Trello Cards in a multithreaded way
    def _fetch_cards(self, num_threads=10, debug=False):
        trello_cards = self.trello_board.all_cards()

        trello_movements_by_card = self._fetch_trello_card_movements_by_card()
        trello_comments_by_card = self._fetch_trello_comments_by_card()

        lists = self.lists.all()

        trello_cycle_dict = {list_.uuid: True for list_ in self.cycle_time_lists()}
        trello_lead_dict = {list_.uuid: True for list_ in self.lead_time_lists()}
        done_list = lists.get(type="done")

        card_dict = {}

        # Definition of the work each thread must do
        # that is the fetch of some cards
        def fetch_card_worker(my_trello_cards):
            for my_trello_card in my_trello_cards:
                must_retry = True
                while must_retry:
                    try:
                        my_trello_card.fetch(eager=False)
                        my_trello_card.actions = trello_movements_by_card.get(my_trello_card.id, [])
                        my_trello_card._comments = trello_comments_by_card.get(my_trello_card.id, [])
                        card_i = self._fetch_card(my_trello_card, lists, done_list, trello_lead_dict, trello_cycle_dict)
                        if debug:
                            print(u"{0} done".format(card_i.uuid))
                        must_retry = False
                        card_dict[card_i.uuid] = card_i
                    except ResourceUnavailable:
                        must_retry = True

        # Work assignment for each thread
        threads = []
        trello_card_chunks = numpy.array_split(trello_cards, num_threads)
        for i in range(0, num_threads):
            fetcher = threading.Thread(target=fetch_card_worker, args=(trello_card_chunks[i],))
            threads.append(fetcher)
            fetcher.start()

        for thread in threads:
            thread.join()

        return card_dict.values()

    # Fetch the cards of this board
    def _create_cards(self, cards, debug=False):

        lists = self.lists.all()

        workflows = self.workflows.all()

        # List reports
        list_report_dict = {list_.uuid: ListReport(list=list_, forward_movements=0, backward_movements=0)
                            for list_ in lists}

        # Member report
        member_report_dict = {member.uuid: MemberReport(board=self, member=member) for member in
                              self.members.all()}

        # Card stats computation
        for card in cards:
            card.save()
            card.create_daily_spent_times()

            trello_card = card.trello_card
            for list_ in lists:
                list_uuid = list_.uuid
                card_stats_by_list = card.stats_by_list[list_uuid]

                if not hasattr(list_report_dict[list_uuid], "times"):
                    list_report_dict[list_uuid].times = []
                list_report_dict[list_uuid].times.append(card_stats_by_list["time"])

                # Update total forward and backward movements
                list_report_dict[list_uuid].forward_movements += card_stats_by_list["forward_moves"]
                list_report_dict[list_uuid].backward_movements += card_stats_by_list["backward_moves"]

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
                member_report.forward_movements += math.ceil(1. * card.forward_movements / 1. * num_trello_card_members)

                # Backward movements of the cards
                if member_report.backward_movements is None:
                    member_report.backward_movements = 0
                member_report.backward_movements += math.ceil(1. * card.backward_movements / 1. * num_trello_card_members)

                # Inform this member report has data and must be saved
                member_report.present = True

                # Card time
                if not hasattr(member_report, "card_times"):
                    member_report.card_times = []
                if card.time is not None:
                    member_report.card_times.append(card.time)

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

    def _fetch_card(self, trello_card, lists, done_list, trello_lead_dict, trello_cycle_dict):
        card = Card.factory_from_trello_card(trello_card, self)
        card.get_stats_by_list(lists, done_list)

        # Total forward and backward movements of a card
        card.forward_movements = 0
        card.backward_movements = 0
        card.time = 0

        # List reports. For each list compute the number of forward movements and backward movements
        # being it its the source.
        # Thus, compute the time the cards live in this list.
        for list_ in lists:
            list_uuid = list_.uuid
            card_stats_by_list = card.stats_by_list[list_uuid]

            card.time += card_stats_by_list["time"]

            # Update total forward and backward movements
            card.forward_movements += card_stats_by_list["forward_moves"]
            card.backward_movements += card_stats_by_list["backward_moves"]

        # Cycle and Lead times
        if trello_card.idList == done_list.uuid:
            card.lead_time = sum(
                [list_stats["time"] if list_uuid in trello_lead_dict else 0 for list_uuid, list_stats in
                 card.stats_by_list.items()])

            card.cycle_time = sum(
                [list_stats["time"] if list_uuid in trello_cycle_dict else 0 for list_uuid, list_stats in
                 card.stats_by_list.items()])

        return card

    # Return the trello board, calling the Trello API.
    def _get_trello_board(self):
        trello_client = self.creator.trello_client
        trello_board = TrelloBoard(client=trello_client, board_id=self.uuid)
        trello_board.fetch()
        return trello_board

    # Return the comments of the board grouped by the uuid of each card
    def _fetch_trello_comments_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="commentCard")
        return comments_by_card

    # Return the card movements of the board grouped by the uuid of each card
    def _fetch_trello_card_movements_by_card(self):
        comments_by_card = self._fetch_trello_actions_by_card(action_filter="updateCard:idList")
        return comments_by_card

    # Return the actions of the board grouped by the uuid of each card
    def _fetch_trello_actions_by_card(self, action_filter, limit=1000):
        # Fetch as long as there is a result
        actions = []
        retry = True
        since = None
        while retry:
            actions += self.trello_board.fetch_actions(action_filter, limit, since)
            retry = len(actions) == limit
            # Dangerous assumption: we are assuming the cards are sorted by date (in descendant order) and thus,
            # we can get the greatest date to ask for more actions since that date.
            since = actions[0]["date"]

        # Group actions by card
        actions_by_card = {}
        for action in actions:
            card_uuid = action[u"data"][u"card"][u"id"]
            if card_uuid not in actions_by_card:
                actions_by_card[card_uuid] = []
            actions_by_card[card_uuid].append(action)
        # Return the actions grouped by card
        return actions_by_card


# Card of the task board
class Card(ImmutableModel):
    COMMENT_SPENT_ESTIMATED_TIME_REGEX = r"^plus!\s+(\-(?P<days_before>(\d+))d\s+)?(?P<spent>(\-)?\d+(\.\d+)?)/(?P<estimated>(\-)?\d+(\.\d+)?)(\s*(?P<description>.+))?"

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

    forward_movements = models.PositiveIntegerField(verbose_name=u"Forward movements of this card", default=0)
    backward_movements = models.PositiveIntegerField(verbose_name=u"Backward movements of this card", default=0)
    time = models.DecimalField(verbose_name=u"Time this card is alive in the board",
                               help_text=u"Time this card is alive in the board in seconds.",
                               decimal_places=4, max_digits=12,
                               default=0)

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
        comment_summary = card.comment_stats()

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

    # Fetch comments of this card
    def comment_stats(self):
        self.comments = self.trello_card.comments

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
        self._daily_spent_times = []
        member_dict = {}
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
                date = local_timezone.localize(datetime.strptime(comment["date"],
                                                                          '%Y-%m-%dT%H:%M:%S.%fZ')).date()
                # If Plus for Trello comment informs that the time was spent several days ago, we have to substract
                # the days to the date of the comment
                if matches.group("days_before"):
                    date -= timedelta(days=int(matches.group("days_before")))

                if matches.group("description") and matches.group("description").strip():
                    description = matches.group("description")
                else:
                    description = self.name

                # Use of memoization to achieve a better performance when loading members
                if member_uuid not in member_dict:
                    member_dict[member_uuid] = self.board.members.get(uuid=member_uuid)

                # Creation of daily spent times for this card
                daily_spent_time = DailySpentTime(board=self.board, card=self, description=description, member=member_dict[member_uuid], date=date,
                                                  spent_time=spent, estimated_time=estimated)
                self._daily_spent_times.append(daily_spent_time)

        self.comment_summary = {
            "daily_spent_times": self.daily_spent_times,
            "member_uuids": member_uuids.keys(),
            "spent": {"total": total_spent, "by_member": spent_by_member},
            "estimated": {"total": total_estimated, "by_member": estimated_by_member}
        }
        return self.comment_summary

    # Create associated daily spent times
    def create_daily_spent_times(self):
        if not hasattr(self, "daily_spent_times"):
            self.fetch_comments()

        for daily_spent_time in self._daily_spent_times:
            DailySpentTime.add_daily_spent_time(daily_spent_time)


# Label of the task board
class Label(ImmutableModel):

    name = models.CharField(max_length=128, verbose_name=u"Name of the label")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the label", unique=True)
    color = models.CharField(max_length=128, verbose_name=u"Color of the label", default=None, null=True)
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





