# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import re
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

import numpy
import requests
import shortuuid
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import Avg, Sum, Min, Max
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils import timezone

from isoweek import Week

from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.niko_niko_calendar.models import DailyMemberMood
from djangotrellostats.apps.notifications.models import Notification
from djangotrellostats.apps.reports.models import CardMovement, CardReview


# Abstract model that represents the immutable objects
from djangotrellostats.remote_backends.factory import RemoteBackendConnectorFactory
from djangotrellostats.utils.custom_uuid import custom_uuid


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

    description= models.TextField(max_length=128, verbose_name=u"Description of the board", default="", blank=True)

    comments = models.TextField(max_length=128, verbose_name=u"Comments for this board", default="", blank=True)

    uuid = models.CharField(max_length=128, verbose_name=u"External id of the board", unique=True)

    last_activity_datetime = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)

    has_to_be_fetched = models.BooleanField(verbose_name=u"Has to be this board fetched?",
                                            help_text="Select this option if you want to fetch data for this board.",
                                            default=True)

    is_archived = models.BooleanField(verbose_name=u"This board is archived",
                                      help_text=u"Archived boards are not fetched automatically and are ignored",
                                      default=False)

    enable_public_access = models.BooleanField(verbose_name=u"Enable public access to this board",
                                               help_text=u"Only when enabled the users will be able to access",
                                               default=False)

    # Public access code to the board
    public_access_code = models.CharField(max_length=32,
                                          verbose_name=u"External code of the board",
                                          help_text=u"With this code it is possible to access to a view with stats "
                                                    u"of this board", unique=True)

    last_fetch_datetime = models.DateTimeField(verbose_name=u"Last fetch datetime", default=None, null=True)

    members = models.ManyToManyField("members.Member", verbose_name=u"Members", related_name="boards")

    percentage_of_completion = models.DecimalField(
        verbose_name=u"Percentage of completion",
        help_text=u"Percentage of completion of project. Mind the percentage of completion of each requirement.",
        decimal_places=2, max_digits=10, blank=True, default=None, null=True
    )

    estimated_number_of_hours = models.PositiveIntegerField(verbose_name=u"Estimated number of hours to be completed",
                                                            help_text=u"Number of hours in the budget",
                                                            blank=True, default=None, null=True)

    hourly_rates = models.ManyToManyField("hourly_rates.HourlyRate", verbose_name=u"Hourly rates",
                                          related_name="boards", blank=True)

    show_on_slideshow = models.BooleanField(
        verbose_name=u"Should this board be shown on the slideshow?",
        help_text=u"Select this checkbox if you want to show this board in the slideshow",
        default=False)

    # Image that appears in the header of the board views
    header_image = models.ImageField(
        verbose_name=u"Header image", default=None, null=True, blank=True,
        help_text=u"Header image for this board. Optional."
    )

    identicon = models.ImageField(
        verbose_name=u"Identicon", default=None, null=True, blank=True,
        help_text=u"Identicon for this board. It is automatically generated and stored."
    )

    identicon_hash = models.CharField(max_length=256,
                                      verbose_name=u"Identicon hash",
                                      help_text=u"Identicon hash used to know when to update it",
                                      default="", blank=True)


    # Users that can view the board stats and other parameters but cannot change anything
    visitors = models.ManyToManyField(User, verbose_name=u"Visitors of this board", related_name="boards", blank=True)

    # Last time the mood for this project was computed.
    # As the computation only has to be done once a day it serves us as a cache
    last_time_mood_was_computed = models.DateTimeField(verbose_name=u"Last time mood was computed",
                                                       default=None, null=True)

    last_mood_value = models.DecimalField(verbose_name=u"Last mood value",
                                          decimal_places=2, max_digits=10, default=None, null=True)

    background_color = models.CharField(
        verbose_name=u"Background color for this board", help_text=u"Background color for this board in hexadecimal",
        max_length=32, default="196A3E"
    )

    title_color = models.CharField(
        verbose_name=u"Title color for this board", help_text=u"Title color for this board in hexadecimal",
        max_length=32, default="FFFFFF"
    )

    # External or source URL
    url = models.CharField(max_length=255, verbose_name=u"URL of the board", null=True, default=None)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    @property
    def active_lists(self):
        return self.lists.exclude(Q(type="closed")|Q(type="ignored")).order_by("position")

    @property
    def active_cards(self):
        return self.cards.filter(is_closed=False).order_by("position")

    # First list of this board
    @property
    def first_list(self):
        try:
            return self.lists.all().order_by("position")[0]
        except IndexError:
            raise List.DoesNotExist

    # Last list of this board
    @property
    def last_list(self):
        try:
            return self.lists.all().order_by("-position")[0]
        except IndexError:
            raise List.DoesNotExist

    # Number of tasks
    @property
    def number_of_tasks(self):
        return self.cards.filter(is_closed=False).count()

    # Number of done tasks
    @property
    def number_of_done_tasks(self):
        return self.cards.filter(is_closed=False, list__type="done").count()

    # Number of comments
    @property
    def number_of_comments(self):
        return CardComment.objects.filter(card__is_closed=False, card__board=self).count()

    # Last 30 comments
    def last_comments(self, number_of_comments=30):
        return CardComment.objects.filter(card__board=self).\
                   order_by("-last_edition_datetime", "-creation_datetime")[:number_of_comments]

    # Returns the date of the last fetch in an ISO format
    def get_human_fetch_datetime(self):
        if self.last_fetch_datetime:
            return self.last_fetch_datetime.strftime("%Y-%m-%d")
        return self.last_activity_datetime.strftime("%Y-%m-%d")

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
            if (hourly_rate.end_date and hourly_rate.start_date <= date <= hourly_rate.end_date) or\
                     date >= hourly_rate.start_date:
                return hourly_rate

        return None

    # Is the board in downtime?
    @property
    def is_in_downtime(self):
        return not self.active_cards.filter(Q(list__type="development") | Q(list__type="ready_to_develop")).exists()

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
        return self.last_fetch_datetime is not None or not self.creator.has_trello_profile

    # Lists that are before development (backlog or ready to develop)
    def before_development_lists(self):
        return self.lists.filter(Q(type="backlog") | Q(type="ready_to_develop") | Q(type="ignored"))

    # Lists that are used to compute cycle time
    def cycle_time_lists(self):
        return self.lists.exclude(Q(type="backlog") | Q(type="ready_to_develop") | Q(type="ignored"))

    # Lists that are used to compute lead time
    def lead_time_lists(self):
        return self.lists.exclude(Q(type="ignored"))

    # Informs if the project is on time or it is delayed.
    def on_time(self):
        if self.estimated_number_of_hours is None:
            return True

        total_spent_time = self.get_spent_time()
        return total_spent_time < self.estimated_number_of_hours

    # Compute the percentage of completion according to the number of spent hours in this project and the estimated
    # number of hours in the budget
    def current_percentage_of_completion(self):
        if self.estimated_number_of_hours is None:
            return 0

        return Decimal(100.0) * self.get_spent_time() / self.estimated_number_of_hours

    # Returns the spent time today for this board
    def get_today_spent_time(self):
        now = timezone.now()
        today = now.date()
        return self.get_spent_time(date=today)

    # Returns the spent time.
    # If date parameter is present, computes the spent time on a given date for this board
    # Otherwise, computes the total spent time for this board
    def get_spent_time(self, date=None, member=None):
        daily_spent_times_filter = {}
        if date:
            if type(date) == tuple or type(date) == list:
                daily_spent_times_filter["date__gte"] = date[0]
                daily_spent_times_filter["date__lte"] = date[1]
            else:
                daily_spent_times_filter["date"] = date
        member_filter = {}
        if member:
            member_filter["member"] = member

        spent_time = self.daily_spent_times.\
            filter(**daily_spent_times_filter).\
            filter(**member_filter).\
            aggregate(sum=Sum("spent_time"))["sum"]

        if spent_time is None:
            return 0

        return spent_time

    # Returns the adjusted spent time according to the spent time factor defined in each member
    def get_adjusted_spent_time(self, date=None, member=None):
        daily_spent_times_filter = {}
        if date:
            if type(date) == tuple or type(date) == list:
                daily_spent_times_filter["date__gte"] = date[0]
                daily_spent_times_filter["date__lte"] = date[1]
            else:
                daily_spent_times_filter["date"] = date

        adjusted_spent_time = 0
        if member:
            daily_spent_times_filter["member"] = member

        daily_spent_times = self.daily_spent_times.filter(**daily_spent_times_filter)

        spent_time_factors_by_member_id = {}
        member_dict = {}

        # For each daily spent time, we have to compute its adjusted value getting the right interval of dates of the
        # spent time factors of the corresponding member
        for daily_spent_time in daily_spent_times:

            # Use memoization to improve member spent time factor fetch
            if daily_spent_time.member_id not in member_dict:
                member_dict[daily_spent_time.member_id] = daily_spent_time.member
                spent_time_factors_by_member_id[daily_spent_time.member_id] = daily_spent_time.member.spent_time_factors.all()

            # Compute the adjusted spent time for this measurement (daily spent time)
            adjusted_spent_time_for_daily_spent_time = Member.adjust_daily_spent_time_from_spent_time_factors(
                daily_spent_time=daily_spent_time,
                spent_time_factors=spent_time_factors_by_member_id[daily_spent_time.member_id],
                attribute="spent_time"
            )

            adjusted_spent_time += adjusted_spent_time_for_daily_spent_time

        return adjusted_spent_time

    # Return the spent time on a given week of a year
    def get_weekly_spent_time(self, week, year, member=None):
        # Get the date interval for the given week
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}
        if member:
            spent_time_on_week_filter["member"] = member
        # Filter the daily spent times and sum their spent time
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        # As usual, a None value means 0
        if spent_time is None:
            return 0
        # Otherwise, return the sum of spent times for the given week
        return spent_time

    # Return the adjusted spent time on a given week of a year
    def get_weekly_adjusted_spent_time(self, week, year, member=None):
        # Get the date interval for the given week
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        # Get the adjusted time of that days
        return self.get_adjusted_spent_time(date=(start_date, end_date), member=member)

    # Average spent time in this project per week
    @property
    def average_weekly_spent_time(self):
        spent_time_by_week = self.spent_time_by_week
        # Number of weeks of the project
        num_weeks = len(spent_time_by_week)
        if num_weeks == 0:
            return 0
        # Sum of all time spent per week
        spent_time_sum = Decimal("0.0")
        for spent_time in spent_time_by_week:
            spent_time_sum += spent_time["spent_time"]
        # Average time spent per week
        return Decimal(spent_time_sum) / Decimal(num_weeks)

    # Last weekly spent time in this project
    @property
    def last_weekly_spent_time(self):
        spent_time_by_week = self.spent_time_by_week.order_by("-week_of_year")
        if not spent_time_by_week.exists():
            return 0
        return spent_time_by_week[0]["spent_time"]

    # The number of hours worked in the last month with some work
    @property
    def last_working_month_spent_time(self):
        # Getting last month that had work
        end_working_date = self.get_working_end_date()
        if end_working_date is None:
            return 0
        # Getting the spent time of that month
        end_working_month = end_working_date.month
        end_working_year = end_working_date.year
        spent_time = self.get_monthly_spent_time(month=end_working_month, year=end_working_year)
        return spent_time

    # The number of hours worked in the last month with some work
    @property
    def last_working_month_adjusted_spent_time(self):
        # Getting last month that had work
        end_working_date = self.get_working_end_date()
        if end_working_date is None:
            return 0

        # The last month and year this board had some work
        end_working_month = end_working_date.month
        end_working_year = end_working_date.year

        # Getting the spent time of that month for each member
        adjusted_spent_time = 0
        for member in self.members.filter(is_developer=True):
            daily_spent_times = self.daily_spent_times.filter(
                date__month=end_working_month,
                date__year=end_working_year,
                member=member
            )
            for daily_spent_time in daily_spent_times:
                adjusted_spent_time += member.adjust_daily_spent_time(daily_spent_time, "spent_time")

        return adjusted_spent_time

    # Return spent time per week
    @property
    def spent_time_by_week(self):
        return self.daily_spent_times.values('week_of_year').annotate(spent_time=Sum("spent_time")).order_by("week_of_year")

    # Return the spent time on a given month of a year
    def get_monthly_spent_time(self, month, year, member=None):
        spent_time_on_week_filter = {"date__month": month, "date__year": year}
        if member:
            spent_time_on_week_filter["member"] = member
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Return the adjusted spent time in this month
    def get_monthly_adjusted_spent_time(self, month, year, member=None):
        first_day_of_month = datetime.date(year=year, month=month, day=1)
        last_day_of_month = first_day_of_month + relativedelta(months=1) - timedelta(days=1)
        return self.get_adjusted_spent_time(date=(first_day_of_month, last_day_of_month), member=member)

    # Returns the spent time.
    # If date parameter is present, computes the spent time on a given date for this board
    # Otherwise, computes the total spent time for this board
    def get_developed_value(self, date=None, member=None):
        daily_spent_times_filter = {}
        if date:
            if type(date) == tuple or type(date) == list:
                daily_spent_times_filter["date__gte"] = date[0]
                daily_spent_times_filter["date__lte"] = date[1]
            else:
                daily_spent_times_filter["date"] = date

        if member:
            daily_spent_times_filter["member"] = member

        developed_value = self.daily_spent_times.filter(**daily_spent_times_filter).aggregate(sum=Sum("rate_amount"))["sum"]
        if developed_value is None:
            return 0
        return developed_value

    # Returns the adjusted developed value according to the spent time factor defined in each member
    def get_adjusted_developed_value(self, date=None, member=None):
        daily_spent_times_filter = {}
        if date:
            if type(date) == tuple or type(date) == list:
                daily_spent_times_filter["date__gte"] = date[0]
                daily_spent_times_filter["date__lte"] = date[1]
            else:
                daily_spent_times_filter["date"] = date

        adjusted_developed_value = 0
        if member:
            daily_spent_times_filter["member"] = member

        daily_spent_times = self.daily_spent_times.filter(**daily_spent_times_filter)
        member_dict = {}
        for daily_spent_time in daily_spent_times:
            if daily_spent_time.member_id not in member_dict:
                member_dict[daily_spent_time.member_id] = daily_spent_time.member
            member = member_dict[daily_spent_time.member_id]
            adjusted_developed_value += member.adjust_daily_spent_time(daily_spent_time, "rate_amount")
        return adjusted_developed_value

    # Informs what is the first day the team worked in this project
    def get_working_start_date(self):
        first_spent_time_date = self.daily_spent_times.all().aggregate(min_date=Min("date"))["min_date"]
        first_card_movement = self.card_movements.all().aggregate(min_datetime=Min("datetime"))["min_datetime"]
        if first_spent_time_date and first_card_movement:
            if first_spent_time_date < first_card_movement.date():
                return first_spent_time_date
            return first_card_movement.date()
        elif first_spent_time_date:
            return first_spent_time_date
        if first_card_movement:
            return first_card_movement.date()
        return None

    # Informs what is the last day the team has been working in this project
    def get_working_end_date(self):
        last_spent_time_date = self.daily_spent_times.all().aggregate(max_date=Max("date"))["max_date"]
        last_card_movement = self.card_movements.all().aggregate(max_datetime=Max("datetime"))["max_datetime"]
        if last_spent_time_date and last_card_movement:
            if last_spent_time_date > last_card_movement.date():
                return last_spent_time_date
            return last_card_movement.date()
        elif last_spent_time_date:
            return last_spent_time_date
        if last_card_movement:
            return last_card_movement.date()
        return None

    # Has this project assessed Python code?
    @property
    def has_python_assessment_report(self):
        return self.pylint_messages.all().exists()

    # Has this project assessed PHP code?
    @property
    def has_php_assessment_report(self):
        return self.phpmd_messages.all().exists()

    # Compute the mood for this project
    @property
    def mood(self):
        mood_value = self.mood_value
        if mood_value > 0:
            return "happy"
        if mood_value == 0:
            return "normal"
        if mood_value < 0:
            return "sad"

    # Compute the mood value for this project
    @property
    def mood_value(self):

        # Check if the value in cache is less than one day old
        now = timezone.now()
        if self.last_time_mood_was_computed is not None and\
                self.last_mood_value is not None and now - self.last_time_mood_was_computed < timedelta(days=1):
            return self.last_mood_value

        members = self.members.filter(is_developer=False)

        start_date = self.get_working_start_date()
        end_date = self.get_working_start_date()
        date_i = copy.deepcopy(start_date)

        for member in members:
            member.moods = []

        while date_i <= end_date:
            for member in members:
                try:
                    member_mood_value = member.daily_member_moods.get(date=date_i).mood_value
                    member.moods.append(member_mood_value)
                except DailyMemberMood.DoesNotExist:
                    pass
            date_i += timedelta(days=1)

        member_mood = []
        for member in members:
            if len(member.moods) > 0:
                member_mood.append(numpy.mean(member.moods))

        if len(member_mood) > 0:
            self.last_mood_value = numpy.mean(member_mood)
        else:
            self.last_mood_value = 0

        self.last_time_mood_was_computed = timezone.now()
        self.save()
        return self.last_mood_value

    # Archive this board
    def archive(self):
        self.is_archived = True
        self.save()

    # Un-archive this board
    def unarchive(self):
        self.is_archived = False
        self.save()

    # Create a new board
    @staticmethod
    def new(member, board):
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.new_board(board)

    # Remove a member from this board
    @transaction.atomic
    def remove_member(self, member, member_to_remove):
        self.members.remove(member_to_remove)
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.remove_member(board=self, member_to_remove=member_to_remove)
        return member_to_remove

    # Add a new member to this board
    @transaction.atomic
    def add_member(self, member, member_to_add):
        self.members.add(member_to_add)
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.add_member(board=self, member_to_add=member_to_add)
        return member_to_add

    # Create a new list
    @transaction.atomic
    def new_list(self, member, new_list):
        connector = RemoteBackendConnectorFactory.factory(member)
        new_list = connector.new_list(new_list)
        new_list.save()
        return new_list

    @transaction.atomic
    def edit_list(self, member, edited_list):
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.edit_list(edited_list)
        edited_list.save()
        return edited_list

    # Delete all cached charts of this board
    def clean_cached_charts(self):
        self.cached_charts.all().update(is_expired=True)

    # Save this board:
    # Assigns a new public_access_code if is not present
    def save(self, *args, **kwargs):
        # Creation of public access code in case there is none present
        if not self.public_access_code:
            self.public_access_code = shortuuid.ShortUUID().random(length=20).lower()
        # Call to parent save method
        super(Board, self).save(*args, **kwargs)


# Card of the task board
class Card(models.Model):

    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"
        index_together = (
            ("board", "creation_datetime", "list"),
            ("board", "creation_datetime"),
            ("board", "list", "position"),
        )

    COMMENT_SPENT_ESTIMATED_TIME_REGEX = r"^plus!\s+(\-(?P<days_before>(\d+))d\s+)?(?P<spent>(\-)?\d+(\.\d+)?)/(?P<estimated>(\-)?\d+(\.\d+)?)(\s*(?P<description>.+))?"
    COMMENT_SPENT_ESTIMATED_TIME_PATTERN = "plus! {days_ago}{spent_time}/{estimated_time} {description}"

    COMMENT_BLOCKED_CARD_REGEX = r"^blocked\s+by\s+(?P<card_url>.+)$"
    COMMENT_BLOCKED_CARD_PATTERN = "blocked by {card_url}"

    COMMENT_REQUIREMENT_CARD_REGEX = r"^task\s+of\s+requirement\s+(?P<requirement_code>.+)$"
    COMMENT_REQUIREMENT_CARD_PATTERN = "task of requirement {requirement_code}"

    COMMENT_REVIEWED_BY_MEMBERS_REGEX = r"^reviewed\s+by\s+(?P<member_usernames>((@[\w\d]+)(\s|,|and)*)+(\s*:\s*(?P<description>.+))?)$"
    COMMENT_REVIEWED_BY_MEMBERS_PATTERN = "reviewed by {member_usernames}"
    COMMENT_REVIEWED_BY_MEMBERS_WITH_DESCRIPTION_PATTERN = "reviewed by {member_usernames}: {description}"

    COMMENT_REVIEWED_BY_MEMBERS_FINDALL_REGEX = r"@[\w\d]+"

    COMMENT_VALUATED_CARD_REGEX = r"^task\s+valued\s+on\s+(?P<value>\d+)$"
    COMMENT_VALUATED_CARD_PATTERN = "task valued on {value}"

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cards")
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="cards")

    name = models.TextField(verbose_name=u"Name of the card")
    uuid = models.CharField(max_length=128, verbose_name=u"External id of the card", unique=True)
    url = models.CharField(max_length=255, verbose_name=u"URL of the card", unique=True)
    short_url = models.CharField(max_length=128, verbose_name=u"Short URL of the card", unique=True)
    description = models.TextField(verbose_name=u"Description of the card")
    is_closed = models.BooleanField(verbose_name=u"Is this card closed?", default=False)
    position = models.PositiveIntegerField(verbose_name=u"Position in the list")
    number_of_comments = models.PositiveIntegerField(verbose_name=u"Number of comments of this card", default=0)
    number_of_reviews = models.PositiveIntegerField(verbose_name=u"Number of reviews of this card", default=0)
    value = models.PositiveIntegerField(verbose_name=u"Value of this card for the client", blank=True, default=None, null=True)

    due_datetime = models.DateTimeField(verbose_name=u"Deadline", blank=True, null=True, default=None)
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")
    last_activity_datetime = models.DateTimeField(verbose_name=u"Last activity datetime")

    number_of_forward_movements = models.PositiveIntegerField(verbose_name=u"Number of forward movements", default=0)
    number_of_backward_movements = models.PositiveIntegerField(verbose_name=u"Number of backward movements", default=0)

    spent_time = models.DecimalField(verbose_name=u"Spent time", decimal_places=4, max_digits=12, default=None,
                                     null=True)

    estimated_time = models.DecimalField(verbose_name=u"Estimated time", decimal_places=4, max_digits=12, default=None,
                                         null=True)

    cycle_time = models.DecimalField(verbose_name=u"Lead time", decimal_places=4, max_digits=12, default=None,
                                     null=True)
    lead_time = models.DecimalField(verbose_name=u"Cycle time", decimal_places=4, max_digits=12, default=None,
                                    null=True)

    valuation_comment = models.OneToOneField("boards.CardComment", related_name="valued_card",
                                             blank=True, default=None, null=True)
    labels = models.ManyToManyField("boards.Label", related_name="cards")
    members = models.ManyToManyField("members.Member", related_name="cards")
    blocking_cards = models.ManyToManyField("boards.card", related_name="blocked_cards")

    def get_lead_time(self):
        if not self.is_done:
            return None
        creation_datetime = self.creation_datetime
        completion_datetime = self.completion_datetime
        time_diff = (completion_datetime - creation_datetime)
        return time_diff.total_seconds() / 3600.0

    def get_cycle_time(self):
        if not self.is_done:
            return None
        try:
            start_development_datetime = \
                self.movements.filter(destination_list__type="development").order_by("datetime")[0].datetime
        except IndexError:
            start_development_datetime = self.creation_datetime
        completion_datetime = self.completion_datetime
        time_diff = (completion_datetime - start_development_datetime)
        return time_diff.total_seconds() / 3600.0

    def get_spent_time(self):
        return self.daily_spent_times.all().aggregate(spent_time_sum=Sum("spent_time"))["spent_time_sum"]

    def get_estimated_time(self):
        return self.daily_spent_times.all().aggregate(estimated_time_sum=Sum("estimated_time"))["estimated_time_sum"]

    # Get the spent time by member for this card
    def get_spent_time_by_member(self, member):
        return self.daily_spent_times.filter(member=member).\
            aggregate(spent_time_sum=Sum("spent_time"))["spent_time_sum"]

    # Get the estimated time by member for this card
    def get_estimated_time_by_member(self, member):
        return self.daily_spent_times.filter(member=member).\
            aggregate(estimated_time_sum=Sum("estimated_time"))["estimated_time_sum"]

    # Return the cards of the boards of an user
    @staticmethod
    def get_user_cards(user, is_archived=False):
        return Card.objects.filter(Q(board__members__user=user)|Q(board__visitors=user), board__is_archived=is_archived)

    # Age of this card as a timedelta
    @property
    def age(self):
        now = timezone.now()
        return now - self.creation_datetime

    @property
    def time_in_each_list(self):

        time_by_list = {list_.id: 0 for list_ in self.board.active_lists.all()}

        movements = self.movements.order_by("datetime")

        card_last_action_datetime = self.creation_datetime

        #  If there are no changes in the card, all its life has been in its creation list
        if not movements.exists():
            card_life_time = (timezone.now() - card_last_action_datetime).total_seconds()
            time_by_list[self.list_id] += card_life_time

        else:
            # Changes in card are ordered to get the dates in order
            last_list = None

            # For each arrival to a list, its datetime will be used to compute the time this card is in
            # that destination list
            for movement in movements:

                time_from_last_list_change = (movement.datetime - card_last_action_datetime).total_seconds()
                time_by_list[movement.source_list_id] += time_from_last_list_change

                # Our last action has been this movement
                card_last_action_datetime = movement.datetime

                # Store the last list
                last_list = movement.destination_list

            # Adding the number of seconds the card has been in its last column (until now)
            # only if the last column is not "Done" column
            if last_list.type != "done":
                time_card_has_spent_in_list_until_now = (timezone.now() - card_last_action_datetime).total_seconds()
                time_by_list[last_list.id] += time_card_has_spent_in_list_until_now\

        return time_by_list

    @property
    def ready_to_develop_datetime(self):
        arrivals_to_ready_to_develop_list = self.movements.filter(destination_list__type="ready_to_develop").order_by("datetime")
        if arrivals_to_ready_to_develop_list.exists():
            return arrivals_to_ready_to_develop_list[0].datetime
        return self.creation_datetime

    @property
    def has_started(self):
        return self.list.type in List.STARTED_CARD_LIST_TYPES

    @property
    def start_datetime(self):
        arrivals_to_in_development_list = self.movements.filter(destination_list__type="development").order_by("datetime")
        if arrivals_to_in_development_list.exists():
            return arrivals_to_in_development_list[0].datetime
        return self.creation_datetime

    @property
    def end_datetime(self):
        arrivals_to_done_list = self.movements.filter(destination_list__type="done").order_by("-datetime")
        if arrivals_to_done_list.exists():
            return arrivals_to_done_list[0].datetime
        return self.creation_datetime

    # Is there any other card that blocks this card?
    @property
    def is_blocked(self):
        return self.blocking_cards.exclude(list__type="done").exists()

    # Cards that are blocking this card and are not done
    @property
    def pending_blocking_cards(self):
        return self.blocking_cards.exclude(list__type="done")

    # Check if this card is done
    @property
    def is_done(self):
        return self.list.type == "done"

    # Forward movements of this card
    @property
    def forward_movements(self):
        return self.movements.filter(type="forward")

    # Backward movements of this card
    @property
    def backward_movements(self):
        return self.movements.filter(type="backward")

    # Number of attachments
    @property
    def number_of_attachments(self):
        return self.attachments.all().count()

    # Returns the adjusted spent time according to the spent time factor defined in each member
    @property
    def adjusted_spent_time(self):
        adjusted_spent_time = 0
        for member in self.members.all():
            daily_spent_times = self.daily_spent_times.filter(member=member)
            for daily_spent_time in daily_spent_times:
                adjusted_spent_time += member.adjust_daily_spent_time(daily_spent_time, "spent_time")

        return adjusted_spent_time

    @property
    def completion_datetime(self):
        if self.list.type != "done":
            raise ValueError(u"This card is not completed")
        try:
            return self.movements.filter(destination_list__type="done").order_by("-id")[0].datetime
        # In case this card is added directly in the "done" list
        except IndexError:
            return self.last_activity_datetime

    # Update cycle/lead cached time according to movements of this card
    def update_lead_cycle_time(self):
        self.lead_time = self.get_lead_time()
        self.cycle_time = self.get_cycle_time()
        self.save()

    # Update spent/estimated cached time according to daily spent time values
    def update_spent_estimated_time(self):
        self.spent_time = self.get_spent_time()
        self.estimated_time = self.get_estimated_time()
        self.save()

    # Update number of card reviews of this card
    def update_number_of_card_reviews(self):
        self.number_of_reviews = self.reviews.all().count()
        self.save()

    # Move this card to the next list
    @transaction.atomic
    def move_forward(self, member):
        next_list = self.list.next_list
        self.move(member=member, destination_list=next_list)

    # Move this card to the previous list
    @transaction.atomic
    def move_backward(self, member):
        previous_list = self.list.previous_list
        self.move(member=member, destination_list=previous_list)

    # Move this card to a random list
    @transaction.atomic
    def move(self, member, destination_list, destination_position="top", local_move_only=False):
        # Only move the card if the source list is different from the destination list.
        # Otherwise only a ordering is needed on the current card list.
        if self.list.id == destination_list.id:
            raise ValueError(u"Trying to move a card to its list")

        # Checking if it is a forward or backward movement
        if self.list.position < destination_list.position:
            movement_type = "forward"
        elif self.list.position > destination_list.position:
            movement_type = "backward"
        else:
            raise ValueError(u"Trying to move a card to its list")

        # Store the movement of this card
        card_movement = CardMovement(
            board=self.board, card=self, type=movement_type, member=member,
            source_list=self.list, destination_list=destination_list, datetime=timezone.now()
        )
        card_movement.save()

        # Update movement count
        # Remember that this card saves the movement count in its attributes
        self.update_movement_count(commit=False)

        # Move the card
        self.list = destination_list
        self.save()

        # Call to trello API
        if not local_move_only:
            connector = RemoteBackendConnectorFactory.factory(member)
            connector.move_card(card=self, destination_list=destination_list)

        # Move to the required position
        self.change_order(member, destination_position=destination_position, local_move_only=local_move_only)

        # Notify the movement to members
        Notification.move_card(mover=member, card=self, board=self.board)

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

    # Change the order of this card in the same list it currently is
    @transaction.atomic
    def change_attribute(self, member, attribute, value):
        connector = RemoteBackendConnectorFactory.factory(member)

        if attribute == "name":
            self.name = value
            connector.set_card_name(value)

        elif attribute == "description":
            self.description = value
            connector.set_card_description(value)

        elif attribute == "is_closed":
            self.is_closed = value
            connector.set_card_is_closed(value)

        elif attribute == "due_datetime":
            if value is not None:
                self.due_datetime = value
                self.save()
                connector.set_due_datetime(self, member)
            else:
                self.due_datetime = None
                self.remove_due_datetime(self, member)

        elif attribute == "value":
            self.change_value(member, value)

        else:
            raise AssertionError("Attribute {0} change not implemented choose one of name, description, is_closed or due_datetime")

        self.save()

    # Change the order of this card in the same list it currently is
    @transaction.atomic
    def change_order(self, member, destination_position="top", local_move_only=False):
        destination_list_cards = self.list.active_cards
        if destination_list_cards.exists():
            # Assigning position to the card
            # If This card is on top, get the old top an move it down
            if destination_position == "top":
                first_card_in_destination_list = destination_list_cards.order_by("position")[0]
                destination_position_value = first_card_in_destination_list.position - 10
                if destination_position_value < 0:
                    destination_position_value = 1
            # If This card is on the bottom, get the old bottom an move it up
            elif destination_position == "bottom":
                first_card_in_destination_list = destination_list_cards.order_by("-position")[0]
                destination_position_value = first_card_in_destination_list.position + 10
            # Otherwise do nothing
            else:
                destination_position_value = destination_position

            # Saving the changes in the card
            self.position = destination_position_value
            self.save()

            # Call to Trello API to order the card
            if not local_move_only:
                connector = RemoteBackendConnectorFactory.factory(member)
                connector.order_card(card=self, position=destination_position_value)

    # Add spent/estimated time
    @transaction.atomic
    def add_spent_estimated_time(self, member, spent_time, estimated_time=None, days_ago=None, description=None):

        # By default this spent/estimated time description is this card's name
        if description is None:
            description = self.name

        # Getting the date of the spent/estimated time
        today = timezone.now().date()
        date = today
        if days_ago is not None:
            date = date - timedelta(days=days_ago)

        # Adding spent time to the card
        if spent_time is not None:
            if self.spent_time is None:
                self.spent_time = 0
            self.spent_time += Decimal(spent_time)
        else:
            spent_time = Decimal(0.0)

        # Adding estimated time to the card
        if estimated_time is None:
            estimated_time = Decimal(spent_time)

        if self.estimated_time is None:
            self.estimated_time = 0

        self.estimated_time += Decimal(estimated_time)

        # Updating the card
        self.save()

        # Preparation of the comment content with the style of Plus for Trello
        days_ago_str = ""
        if days_ago:
            days_ago_str = "-{0}d ".format(days_ago)

        # Creation of comment with the daily spent time
        comment_content = Card.COMMENT_SPENT_ESTIMATED_TIME_PATTERN.format(
            days_ago=days_ago_str, spent_time=spent_time, estimated_time=estimated_time, description=description
        )

        comment = self.add_comment(member, comment_content)

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

    # Add a new blocking card to this card
    @transaction.atomic
    def add_blocking_card(self, member, blocking_card):
        comment_content = Card.COMMENT_BLOCKED_CARD_PATTERN.format(card_url=blocking_card.url)
        comment = self.add_comment(member, comment_content)

    # Remove a blocking card of this card
    @transaction.atomic
    def remove_blocking_card(self, member, blocking_card):
        self.delete_comment(member, blocking_card.blocking_comments.get(card=self))

    # Add a review to this card
    @transaction.atomic
    def add_review(self, member, reviewers, description=""):
        # Add the blocking card with the review format
        member_usernames = ", ".join(["@{0}".format(reviewer.external_username) for reviewer in reviewers])
        if description:
            content = Card.COMMENT_REVIEWED_BY_MEMBERS_WITH_DESCRIPTION_PATTERN.format(
                member_usernames=member_usernames,
                description=description
            )
        else:
            content = Card.COMMENT_REVIEWED_BY_MEMBERS_PATTERN.format(
                member_usernames=member_usernames
            )

        self.add_comment(member, content)

    # Deletion of review
    @transaction.atomic
    def delete_review(self, member, review):
        self.delete_comment(member, review.comment)

    # Add a requirement to this card
    @transaction.atomic
    def add_requirement(self, member, requirement):
        # Add the requirement with the comment format
        comment_content = Card.COMMENT_REQUIREMENT_CARD_PATTERN.format(requirement_code=requirement.code)
        self.add_comment(member, comment_content)

    # Removing a requirement of this card
    @transaction.atomic
    def remove_requirement(self, member, requirement):
        comment = self.comments.get(requirement=requirement)
        self.delete_comment(member, comment)

    # Changing the value of this card
    @transaction.atomic
    def change_value(self, member, value):

        try:
            valuation_comment = self.valuation_comment
        except CardComment.DoesNotExist:
            valuation_comment = None

        if value is not None:
            comment_content = Card.COMMENT_VALUATED_CARD_PATTERN.format(value=value)
            if valuation_comment is not None:
                # Edition of comment with the valuation of this card
                self.edit_comment(member, comment=valuation_comment, new_content=comment_content)
                self.value = value
            else:
                # Creation of comment with the valuation of this card
                self.valuation_comment = self.add_comment(member, comment_content)
            self.save()
        else:
            if valuation_comment is not None:
                self.delete_comment(member, comment=valuation_comment)
                self.save()

                # Add a new comment to this card

    # Adds a new attachment to this card
    @transaction.atomic
    def add_attachment(self, member, attachment):

        # Create comment locally using the id of the new comment in Trello
        attachment.card = self

        connector = RemoteBackendConnectorFactory.factory(member)
        attachment = connector.add_attachment_to_card(card=self, attachment=attachment)
        attachment.save()

        # Returning the attachment because it can be needed
        return attachment

    # Adds a new attachment to this card
    @transaction.atomic
    def add_new_attachment(self, member, uploaded_file, uploaded_file_name=None):
        attachment = CardAttachment(card=self, uuid=custom_uuid(),
                                    uploader=member, is_cover=False, creation_datetime=timezone.now())
        attached_file = File(uploaded_file)
        if uploaded_file_name is None:
            uploaded_file_name = uploaded_file.name

        # If there is already a file named uploaded_file_name, put
        if CardAttachment.objects.filter(file=uploaded_file_name).exists():
            matches = re.match("^(?P<filename>.+)(?P<extension>\.[\w\d]+)", uploaded_file_name)
            if matches:
                filename = matches.group("filename")
                extension = matches.group("extension")
                now = timezone.now()
                uploaded_file_name = "{0}-{1}{2}".format(filename, now.isoformat(), extension)

        attachment.file.save(uploaded_file_name, attached_file)
        return self.add_attachment(member, attachment)

    # Delete an existing attachment of this card
    @transaction.atomic
    def delete_attachment(self, member, attachment):
        # Delete remote attachment
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.delete_attachment_of_card(card=self, attachment=attachment)

        # Delete attachment locally
        attachment.delete()

    # Add a new comment to this card
    @transaction.atomic
    def add_comment(self, member, content):

        # Create comment locally using the id of the new comment in Trello
        card_comment = CardComment(card=self, author=member, content=content,
                                   creation_datetime=timezone.now())

        connector = RemoteBackendConnectorFactory.factory(member)
        card_comment = connector.add_comment_to_card(card=self, comment=card_comment)
        card_comment.save()

        # Increment the number of comments
        self.number_of_comments += 1
        self.save()

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

        # Returning the comment because it can be needed
        return card_comment

    # Edit a card comment
    @transaction.atomic
    def edit_comment(self, member, comment, new_content):
        if member.uuid != comment.author.uuid:
            raise AssertionError(u"This comment does not belong to {0}".format(member.external_username))

        comment.content = new_content
        comment.last_edition_datetime = timezone.now()

        connector = RemoteBackendConnectorFactory.factory(member)
        comment = connector.edit_comment_of_card(card=self, comment=comment)
        comment.save()

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

        # Returning the comment because it can be needed
        return comment

    # Delete an existing comment of this card
    @transaction.atomic
    def delete_comment(self, member, comment):
        # Delete remote comment
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.delete_comment_of_card(card=self, comment=comment)

        # Delete comment locally
        comment.delete()

        # Decrement the number of comments
        self.number_of_comments -= 1
        self.save()

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

    # Update labels of the card
    @transaction.atomic
    def update_labels(self, member, labels):
        connector = RemoteBackendConnectorFactory.factory(member)

        # New labels
        for label in labels:
            if not self.labels.filter(id=label.id).exists():
                self.labels.add(label)
                connector.add_label_to_card(card=self, label=label)

        # Check if there is any label that needs to be removed
        label_ids = {label.id: label for label in labels}
        for card_label in self.labels.all():
            if card_label.id not in label_ids:
                self.labels.remove(card_label)
                connector.remove_label_of_card(card=self, label=card_label)

        # Delete all cached charts for this board
        self.board.clean_cached_charts()

    # Updates the number of movements of this card
    def update_movement_count(self, commit=True):
        self.number_of_forward_movements = self.forward_movements.count()
        self.number_of_backward_movements = self.backward_movements.count()
        if commit:
            self.save()


# Card attachment
class CardAttachment(models.Model):
    class Meta:
        verbose_name = "Card attachment"
        verbose_name_plural = "Card attachments"
        index_together = (
            ("card", "creation_datetime", "uploader"),
            ("uploader", "card", "creation_datetime"),
            ("card", "uploader", "creation_datetime"),
            ("creation_datetime", "card", "uploader"),
        )

    uuid = models.CharField(max_length=128, verbose_name=u"External id of this attachment", unique=True)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card this attachment belongs to",
                             related_name="attachments")
    uploader = models.ForeignKey("members.Member", verbose_name=u"Member uploader of this attachment",
                                 related_name="attachments")
    external_file_url = models.CharField(verbose_name=u"External file URL", max_length=1024, default="", blank=True)
    external_file_name = models.CharField(verbose_name=u"External file name", max_length=128, default="", blank=True)
    file = models.FileField(verbose_name=u"File content", null=True, blank=True, default=None)
    is_cover = models.BooleanField(
        verbose_name=u"Is this file the cover of the card?",
        help_text="Is this file the cover of the card? "
                  "If it is the cover, it will be used as a the header image of the card.",
        default=True
    )
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime of the comment")

    def fetch_external_file(self):
        if self.external_file_url and not self.file:
            if self.external_file_name == "":
                self.external_file_name = custom_uuid()
            file_content_request = requests.get(self.external_file_url)
            self.file.save(self.external_file_name, ContentFile(file_content_request.text))
            self.save()


# Each one of the comments made by members in each card
class CardComment(models.Model):

    class Meta:
        verbose_name = "Card comment"
        verbose_name_plural = "Card comments"
        index_together = (
            ("card", "creation_datetime", "author"),
            ("author", "card", "creation_datetime"),
            ("card", "author", "creation_datetime"),
            ("creation_datetime", "card", "author"),
        )

    uuid = models.CharField(max_length=128, verbose_name=u"External id of the comment of this comment", unique=True)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card this comment belongs to", related_name="comments")
    author = models.ForeignKey("members.Member", verbose_name=u"Member author of this comment", related_name="comments")
    content = models.TextField(verbose_name=u"Content of the comment")
    blocking_card = models.ForeignKey("boards.Card", verbose_name=u"Blocking card this comment belongs to", related_name="blocking_comments", null=True, default=None)
    review = models.OneToOneField("reports.CardReview", verbose_name=u"Card review this comment represents", related_name="comment", null=True, default=None)
    requirement = models.ForeignKey("requirements.Requirement", verbose_name=u"Requirement this comment belongs to", related_name="card_comments", null=True, default=None)
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime of the comment")
    last_edition_datetime = models.DateTimeField(verbose_name=u"Last edition of the comment", default=None, null=True)

    def get_spent_estimated_time_from_content(self):
        matches = re.match(Card.COMMENT_SPENT_ESTIMATED_TIME_REGEX, self.content, re.IGNORECASE)
        if matches:
            date = self.creation_datetime.date()

            if matches.group("days_before"):
                date -= timedelta(days=int(matches.group("days_before")))

            if matches.group("description") and matches.group("description").strip():
                description = matches.group("description")
            else:
                description = self.card.name

            return {
                "date":  date,
                "spent_time": float(matches.group("spent")),
                "estimated_time": float(matches.group("estimated")),
                "description": description
            }
        return None

    # Returns the blocking card linked to this comment extracted from its content.
    # If it is not a blocking card comment, return None
    @property
    def blocking_card_from_content(self):
        matches = re.match(Card.COMMENT_BLOCKED_CARD_REGEX, self.content, re.IGNORECASE)
        if matches:
            blocking_card_url = matches.group("card_url")
            blocking_card = self.card.board.cards.get(url=blocking_card_url)
            return blocking_card
        return None

    # Return the requirement linked to this comment extracted from its content.
    # If it is not a requirement card comment, return None.
    @property
    def requirement_from_content(self):
        matches = re.match(Card.COMMENT_REQUIREMENT_CARD_REGEX, self.content, re.IGNORECASE)
        if matches:
            requirement_code = matches.group("requirement_code")
            requirement = self.card.board.requirements.get(code=requirement_code)
            return requirement
        return None

    # Return the reviewer members of this comment extracted from its content.
    # If it is not a reviewer card comment, return None.
    @property
    def review_from_comment(self):
        matches = re.match(Card.COMMENT_REVIEWED_BY_MEMBERS_REGEX, self.content, re.IGNORECASE)
        if matches:
            # Extracting member usernames
            member_usernames_string = matches.group("member_usernames")
            member_usernames = re.findall(Card.COMMENT_REVIEWED_BY_MEMBERS_FINDALL_REGEX, member_usernames_string)
            if len(member_usernames) == 1 and member_usernames[0] == "@board":
                members = self.card.board.members.all()
            else:
                cleaned_member_usernames = [member_username.replace("@", "") for member_username in member_usernames]
                members = [member for member in self.card.board.members.filter(trello_member_profile__username__in=cleaned_member_usernames)]
            # Checkout the description of the review
            try:
                description = matches.group("description")
            except IndexError:
                description = ""

            # Construct a dict with the review info
            _review_from_comment = {"reviewers": members, "datetime": self.creation_datetime, "card": self.card, "board": self.card.board, "description": description}
            return _review_from_comment

        return None

    # Return the card value associated to this comment extracted from its content.
    @property
    def card_value_from_content(self):
        matches = re.match(Card.COMMENT_VALUATED_CARD_REGEX, self.content, re.IGNORECASE)
        if matches:
            value = matches.group("value")
            return value
        return None

    def delete(self, *args, **kwargs):
        super(CardComment, self).delete(*args, **kwargs)

        # If the comment is a spent/estimated measure it should be updated
        spent_estimated_time = self.get_spent_estimated_time_from_content()
        if spent_estimated_time:
            self.card.daily_spent_times.filter(spent_time=spent_estimated_time["spent_time"],
                                          estimated_time=spent_estimated_time["estimated_time"]).delete()
            self.card.update_spent_estimated_time()

        # If the comment is a blocking card mention, and is going to be deleted, delete it
        blocking_card = self.blocking_card_from_content
        if blocking_card:
            self.card.blocking_cards.remove(blocking_card)

        # If the comment is a requirement card mention, and is going to be deleted, delete it
        requirement = self.requirement
        if requirement:
            self.card.requirements.remove(requirement)

        # If the comment is a review card mention, and is going to be deleted, delete it
        review = self.review
        if review:
            self.card.reviews.filter(id=review.id).delete()

        # If the comment is a valuation of the card, and is going to be deleted, assign
        # None the value of the card
        try:
            valued_card = self.valued_card
            if valued_card:
                valued_card.value = None
                valued_card.valuation_comment = None
                valued_card.save()
        except Card.DoesNotExist:
            pass

    # Card comment saving
    def save(self, *args, **kwargs):
        card = self.card
        earlier_card_comment_exists = card.comments.filter(uuid=self.uuid).exists()

        if earlier_card_comment_exists:
            earlier_card_comment = card.comments.get(uuid=self.uuid)
            self._save_old(card, earlier_card_comment)
        else:
            self._save_new(card)

        super(CardComment, self).save(*args, **kwargs)

        # If this comment contains S/E time, update the spent and estimated times of the parent card
        if hasattr(self, "daily_spent_time") and self.daily_spent_time and self.daily_spent_time.id is None:
            self.daily_spent_time.save()
            # Update the spent and estimated time
            card.update_spent_estimated_time()

        # If this comment is a review, update the card reviews of the parent card
        elif hasattr(self, "review") and self.review:
            card.update_number_of_card_reviews()

        # If the value given by the comment is different than the current value of the card, update it
        elif hasattr(self, "card_value"):
            card_value = getattr(self, "card_value")
            card.value = card_value
            card.valuation_comment = self
            card.save()

        Notification.add_card_comment(self, card)

    # Save an old comment
    def _save_old(self, card, earlier_card_comment):

        if self.content != earlier_card_comment.content:

            # Is it a spent/estimated time comment?
            spent_estimated_time = self.get_spent_estimated_time_from_content()
            earlier_spent_estimated_time = earlier_card_comment.get_spent_estimated_time_from_content()

            if spent_estimated_time:
                if hasattr(self, "daily_spent_time"):
                    self.daily_spent_time.set_from_comment(self)
                else:
                    self.daily_spent_time = DailySpentTime.create_from_comment(self)
                self.daily_spent_time.save()
                # Update the spent and estimated time
                card.update_spent_estimated_time()

            # Is it a blocking card comment?
            blocking_card = self.blocking_card_from_content
            earlier_blocking_card = earlier_card_comment.blocking_card
            if blocking_card != earlier_blocking_card:
                if earlier_blocking_card is not None:
                    card.blocking_cards.remove(earlier_blocking_card)
                    self.blocking_card = None
                if blocking_card is not None:
                    card.blocking_cards.add(blocking_card)
                    self.blocking_card = blocking_card

            # Is it a requirement card comment?
            requirement = self.requirement_from_content
            earlier_requirement = earlier_card_comment.requirement
            if requirement != earlier_requirement:
                if earlier_requirement is not None:
                    card.requirements.remove(earlier_requirement)
                    self.requirement = None
                if requirement is not None:
                    card.requirements.add(requirement)
                    self.requirement = requirement

            # Is it a review comment?
            review_from_comment = self.review_from_comment
            # If there is a new review in this comment, add or update this review accordingly
            if review_from_comment:
                review_description = review_from_comment.get("description")
                if review_description is None:
                    review_description = ""
                CardReview.update_or_create(self, review_from_comment["reviewers"], review_description)

            # If there is not a review, check if there was an earlier review and in that case, delete it
            elif self.review and self.card.reviews.filter(id=self.review.id).exists():
                self.card.reviews.filter(id=self.review.id).delete()

            # Is it a valued card comment?
            card_value_from_comment = self.card_value_from_content
            if card_value_from_comment is not None:
                self.card_value = card_value_from_comment

    # Save a new comment
    def _save_new(self, card):

        # Is it a spent/estimated time comment?
        spent_estimated_time = self.get_spent_estimated_time_from_content()
        if spent_estimated_time:
            # Creation of Daily Spent Time that depends on this comment
            self.daily_spent_time = DailySpentTime.create_from_comment(self)

        # Is it a blocking card comment?
        blocking_card = self.blocking_card_from_content
        if blocking_card:
            card.blocking_cards.add(blocking_card)
            self.blocking_card = blocking_card

        # Is it a requirement card comment?
        requirement = self.requirement_from_content
        if requirement:
            card.requirements.add(requirement)
            self.requirement = requirement

        # Is it a reviewer card comment?
        review_from_comment = self.review_from_comment
        if review_from_comment:
            reviewer_members = review_from_comment.get("reviewers")
            description = review_from_comment.get("description", "")
            if description is None:
                description = ""
            review = CardReview.create(self, reviewer_members, description)
            self.review = review

        # Is it a valued card comment?
        card_value_from_comment = self.card_value_from_content
        if card_value_from_comment is not None:
            self.card_value = card_value_from_comment

        Notification.add_card_comment(card=card, card_comment=self)


# Label of the task board
class Label(models.Model):

    NATIVE_LABEL_NAMES = [
        ("Aqua", "00FFFF"),
        ("Aquamarine", "7FFFD4"),
        ("Green", "61bd4f"),
        ("Yellow", "f2d600"),
        ("Orange", "ffab4a"),
        ("Red", "eb5a46"),
        ("Brown", "89609E"),
        ("Blue", "0079bf"),
        ("Black", "000000"),
        ("DarkRed", "8B0000")
    ]

    class Meta:
        verbose_name = "label"
        verbose_name_plural = "labels"
        index_together = (
            ("board", "name", "color"),
        )

    name = models.CharField(max_length=128, verbose_name=u"Name of the label")
    uuid = models.CharField(max_length=128, verbose_name=u"External id of the label", unique=True)
    color = models.CharField(max_length=128, verbose_name=u"Color of the label", default=None, null=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="labels")

    def avg_estimated_time(self, **kwargs):
        label_cards = self.cards.filter(**kwargs)
        avg_estimated_time = label_cards.aggregate(avg_estimated_time=Avg("estimated_time"))["avg_estimated_time"]
        return avg_estimated_time

    def avg_spent_time(self, **kwargs):
        label_cards = self.cards.filter(**kwargs)
        avg_spent_time = label_cards.aggregate(avg_spent_time=Avg("spent_time"))["avg_spent_time"]
        return avg_spent_time

    def avg_cycle_time(self, **kwargs):
        avg_cycle_time = self.cards.filter(**kwargs).aggregate(Avg("cycle_time"))["cycle_time__avg"]
        return avg_cycle_time

    def avg_lead_time(self, **kwargs):
        avg_lead_time = self.cards.filter(**kwargs).aggregate(Avg("lead_time"))["lead_time__avg"]
        return avg_lead_time

    @staticmethod
    def create_default_labels(board):
        default_labels = []
        for label_name in Label.NATIVE_LABEL_NAMES:
            label = Label(name=label_name[0], color=label_name[1], uuid=custom_uuid(), board=board)
            label.save()
            default_labels.append(label)
        return default_labels


# List of the task board
class List(models.Model):
    LIST_TYPES = ("ignored", "backlog", "ready_to_develop", "development",
                  "after_development_in_review", "after_development_waiting_release", "done", "closed")
    STARTED_CARD_LIST_TYPES = ("development", "after_development_in_review", "after_development_waiting_release", "done")
    LIST_TYPE_CHOICES = (
        ("ignored", "Ignored"),
        ("backlog", "Backlog"),
        ("ready_to_develop", "Ready to develop"),
        ("development", "In development"),
        ("after_development_in_review", "After development (in review)"),
        ("after_development_waiting_release", "After development (waiting release)"),
        ("done", "Done"),
        ("closed", "Closed"),
    )
    name = models.CharField(max_length=128, verbose_name=u"Name of the list")
    uuid = models.CharField(max_length=128, verbose_name=u"External id of the list", unique=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="lists")
    type = models.CharField(max_length=64, choices=LIST_TYPE_CHOICES, default="ready_to_develop")
    position = models.PositiveIntegerField(verbose_name=u"Position of this list in the board", default=0)
    wip_limit = models.PositiveIntegerField(verbose_name=u"Maximum WIP limit of this list",
                                            help_text=u"Maximum number of cards that should be in this list",
                                            default=None, null=True, blank=True)

    # Adds a new card
    @transaction.atomic
    def add_card(self, member, name, position="bottom"):
        board = self.board

        # Construction of the card
        # We don't save it yet because we need some Trello attributes before saving
        card = Card(board=board, name=name, list=self)
        card.creator = member # TODO: not a model attribute (yet)

        # Update the remote backend
        connector = RemoteBackendConnectorFactory.factory(member)
        card = connector.new_card(card=card, labels=None, position=position)
        card.save()

        return card

    @transaction.atomic
    # Move the position of a list
    def move(self, member, position):
        self.position = position
        self.save()

        connector = RemoteBackendConnectorFactory.factory(member)
        connector.move_list(list=self, position=position)

    # Moves all cards to other list (destination_list)
    @transaction.atomic
    def move_cards(self, member, destination_list):
        if self.id == destination_list.id:
            raise AssertionError(u"Source list and destination list cannot be the same")
        # Card local movement
        cards_to_move = self.active_cards.all()
        for card_to_move in cards_to_move:
            card_to_move.move(member, destination_list, destination_position="top", local_move_only=True)
        # Call to remote API
        connector = RemoteBackendConnectorFactory.factory(member)
        connector.move_list_cards(source_list=self, destination_list=destination_list)

    # Return all cards that are not archived (closed)
    @property
    def active_cards(self):
        return self.cards.filter(is_closed=False).order_by("position")

    # Informs if this list is the first list
    @property
    def is_first(self):
        position_of_first_list = self.board.lists.aggregate(min_position=Min("position"))["min_position"]
        return self.position == position_of_first_list

    # Informs if this list is the last list
    @property
    def is_last(self):
        position_of_last_list = self.board.lists.aggregate(max_position=Max("position"))["max_position"]
        return self.position == position_of_last_list

    # Next list of this list
    @property
    def next_list(self):
        try:
            return self.board.lists.filter(position__gt=self.position).order_by("position")[0]
        except IndexError:
            raise List.DoesNotExist

    # Previous list of this list
    @property
    def previous_list(self):
        try:
            return self.board.lists.filter(position__lt=self.position).order_by("-position")[0]
        except IndexError:
            raise List.DoesNotExist

    # Forward movements that have this list as source
    @property
    def forward_movements_from_this_list(self):
        return self.source_movements.all(type="forward")

    # Backward movements that have this list as source
    # Useful for measuring if this list is a bottleneck
    @property
    def backward_movements_from_this_list(self):
        return self.source_movements.filter(type="backward")

    def card_time_in_list(self, card):
        card_time_in_list = 0

        # If it is the first list, we have to add the time until the first movement
        if self.is_first:
            if card.movements.filter(source_list=self).exists():
                card_first_movement = card.movements.filter(source_list=self).order_by("datetime")[0]
                card_time_in_first_list = (card_first_movement.datetime - card.creation_datetime).seconds
            else:
                card_time_in_first_list = (timezone.now() - card.creation_datetime).seconds
            card_time_in_list += card_time_in_first_list

        # We add the difference in time for the pairs of movements in this list
        # A pair is when this list is destination of a movement and the next movement is leaving this list
        card_movements = card.movements.order_by("datetime")
        for card_movement in card_movements.filter(destination_list=self):
            next_movements = card_movements.filter(source_list=self)
            if next_movements.exists():
                card_time_in_list += (next_movements[0].datetime - card_movement.datetime).seconds
            else:
                card_time_in_list += (timezone.now() - card_movement.datetime).seconds

        return card_time_in_list

    # Average time the cards spend in this list
    @property
    def active_cards_times_in_list(self):
        card_times_in_list = []
        for card in self.board.active_cards:
            card_times_in_list.append(self.card_time_in_list(card))
        return card_times_in_list

    def active_cards_time_in_list(self):
        card_times = self.active_cards_times
        return sum(card_times)

    @property
    def avg_card_time_in_list(self):
        card_times = self.active_cards_times_in_list
        if len(card_times) > 0:
            return numpy.average(card_times, axis=0)
        return 0

    @property
    def std_dev_card_time_in_list(self):
        card_times = self.active_cards_times_in_list
        if len(card_times) > 0:
            return numpy.mean(card_times, axis=0)
        return 0


# Relationship between card and its members
class CardMemberRelationship(models.Model):
    class Meta:
        managed = False
        db_table = "boards_card_members"

    id = models.IntegerField(primary_key=True)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="card_member_relationships")
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="card_member_relationships")

    # Return a dict of members by card
    @staticmethod
    def get_members_by_card(board, member_cache=None):
        if member_cache is None:
            member_cache = {}

        members_by_card = {}
        card_member_relationships = CardMemberRelationship.objects.filter(card__board=board)
        for card_member_relationship in card_member_relationships:

            card_id = card_member_relationship.card_id
            member_id = card_member_relationship.member_id

            if card_id not in members_by_card:
                members_by_card[card_id] = []

            if member_id not in member_cache:
                member_cache[member_id] = card_member_relationship.member

            member = member_cache[card_member_relationship.member_id]
            members_by_card[card_member_relationship.card_id].append(member)

        return members_by_card


# Relationship between card and its labels
class CardLabelRelationship(models.Model):
    class Meta:
        managed = False
        db_table = "boards_card_labels"

    id = models.IntegerField(primary_key=True)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="card_label_relationships")
    label = models.ForeignKey("boards.Label", verbose_name=u"Label", related_name="card_label_relationships")

    # Return a dict of labels by card
    @staticmethod
    def get_labels_by_card(board, label_cache=None):
        if label_cache is None:
            label_cache = {}

        labels_by_card = {}
        card_label_relationships = CardLabelRelationship.objects.filter(card__board=board)
        for card_label_relationship in card_label_relationships:

            card_id = card_label_relationship.card_id
            label_id = card_label_relationship.label_id

            if card_id not in labels_by_card:
                labels_by_card[card_id] = []

            if label_id not in label_cache:
                label_cache[label_id] = card_label_relationship.label

            label = label_cache[card_label_relationship.label_id]
            labels_by_card[card_label_relationship.card_id].append(label)

        return labels_by_card
