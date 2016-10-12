# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from decimal import Decimal

import numpy
import shortuuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Avg, Sum, Min, Max
from django.db.models.query_utils import Q
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.reports.models import CardMovement

# Abstract model that represents the immutable objects
from djangotrellostats.trello_api.cards import move_card, add_comment_to_card


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

    enable_public_access = models.BooleanField(verbose_name=u"Enable public access to this board",
                                               help_text=u"Only when enabled the users will be able to access",
                                               default=False)

    # Public access code to the board
    public_access_code = models.CharField(max_length=32,
                                          verbose_name=u"External code of the board",
                                          help_text=u"With this code it is possible to access to a view with stats "
                                                    u"of this board", unique=True)

    last_fetch_datetime = models.DateTimeField(verbose_name=u"Last fetch datetime", default=None, null=True)

    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="boards")

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
        help_text=u"Mark this checkbox if you want to show this board in the slideshow",
        default=False)

    visitors = models.ManyToManyField(User, verbose_name=u"Visitors of this board", related_name="boards", blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # Number of tasks
    @property
    def number_of_tasks(self):
        return self.cards.filter(is_closed=False).count()

    # Number of done tasks
    @property
    def number_of_done_tasks(self):
        return self.cards.filter(is_closed=False, list__type="done").count()

    @property
    def number_of_comments(self):
        return CardComment.objects.filter(card__is_closed=False, card__board=self).count()

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
    def get_spent_time(self, date=None):
        daily_spent_times_filter = {}
        if date:
            daily_spent_times_filter["date"] = date

        spent_time = self.daily_spent_times.filter(**daily_spent_times_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Returns the adjusted spent time according to the spent time factor defined in each member
    def get_adjusted_spent_time(self, date=None):
        daily_spent_times_filter = {}
        if date:
            daily_spent_times_filter["date"] = date

        adjusted_spent_time = 0
        for member in self.members.all():
            daily_spent_times_filter["member"] = member
            spent_time = self.daily_spent_times.filter(**daily_spent_times_filter).aggregate(sum=Sum("spent_time"))["sum"]
            if spent_time is not None:
                member_adjusted_spent_time = member.spent_time_factor * spent_time
                adjusted_spent_time += member_adjusted_spent_time

        return adjusted_spent_time

    # Return the spent time on a given week of a year
    def get_weekly_spent_time(self, week, year):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Average spent time in this project per week
    @property
    def average_weekly_spent_time(self):
        spent_time_by_week = self.spent_time_by_week
        # Number of weeks of the project
        num_weeks = len(spent_time_by_week)
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
        return spent_time_by_week[0]["spent_time"]

    # Return spent time per week
    @property
    def spent_time_by_week(self):
        return self.daily_spent_times.values('week_of_year').annotate(spent_time=Sum("spent_time")).order_by("week_of_year")

    # Return the spent time on a given month of a year
    def get_monthly_spent_time(self, month, year):
        spent_time_on_week_filter = {"date__month": month, "date__year": year}
        spent_time = self.daily_spent_times.filter(**spent_time_on_week_filter).aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Returns the spent time.
    # If date parameter is present, computes the spent time on a given date for this board
    # Otherwise, computes the total spent time for this board
    def get_developed_value(self, date=None):
        daily_spent_times_filter = {}
        if date:
            daily_spent_times_filter["date"] = date

        developed_value = self.daily_spent_times.filter(**daily_spent_times_filter).aggregate(sum=Sum("rate_amount"))["sum"]
        if developed_value is None:
            return 0
        return developed_value

    # Returns the adjusted developed value according to the spent time factor defined in each member
    def get_adjusted_developed_value(self, date=None):
        daily_spent_times_filter = {}
        if date:
            daily_spent_times_filter["date"] = date

        adjusted_developed_value = 0
        for member in self.members.all():
            daily_spent_times_filter["member"] = member
            developed_value = self.daily_spent_times.filter(**daily_spent_times_filter).aggregate(sum=Sum("rate_amount"))["sum"]
            if developed_value is not None:
                member_adjusted_developed_value = member.spent_time_factor * developed_value
                adjusted_developed_value += member_adjusted_developed_value

        return adjusted_developed_value

    # Informs what is the first day the team started working in this project
    def get_working_start_date(self):
        first_spent_time_date = self.daily_spent_times.all().aggregate(min_date=Min("date"))["min_date"]
        first_card_movement = self.card_movements.all().aggregate(min_datetime=Min("datetime"))["min_datetime"]
        if first_spent_time_date and first_card_movement:
            if first_spent_time_date < first_card_movement.date():
                return first_spent_time_date
            return first_card_movement.date()
        elif first_spent_time_date:
            return first_spent_time_date
        return first_card_movement

    # Informs what is the first day the team started working in this project
    def get_working_end_date(self):
        return self.daily_spent_times.all().aggregate(max_date=Max("date"))["max_date"]

    # Has this project assessed Python code?
    @property
    def has_python_assessment_report(self):
        return self.pylint_messages.all().exists()

    # Has this project assessed PHP code?
    @property
    def has_php_assessment_report(self):
        return self.phpmd_messages.all().exists()

    @property
    def mood(self):
        members = self.members.filter(is_developer=False)
        return numpy.mean([member.mood for member in members])

    def save(self, *args, **kwargs):
        # Creation of public access code in case there is none present
        if not self.public_access_code:
            self.public_access_code=shortuuid.ShortUUID().random(length=20).lower()
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
    COMMENT_REQUIREMENT_CARD_REGEX = r"^task\s+of\s+requirement\s+(?P<requirement_code>.+)$"

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cards")
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="cards")

    name = models.TextField(verbose_name=u"Name of the card")
    uuid = models.CharField(max_length=128, verbose_name=u"External id of the card", unique=True)
    url = models.CharField(max_length=255, verbose_name=u"URL of the card", unique=True)
    short_url = models.CharField(max_length=128, verbose_name=u"Short URL of the card", unique=True)
    description = models.TextField(verbose_name=u"Description of the card")
    is_closed = models.BooleanField(verbose_name=u"Is this card closed?", default=False)
    position = models.PositiveIntegerField(verbose_name=u"Position in the list")
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")
    last_activity_datetime = models.DateTimeField(verbose_name=u"Last activity datetime")

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
    members = models.ManyToManyField("members.Member", related_name="cards")
    blocking_cards = models.ManyToManyField("boards.card", related_name="blocked_cards")

    # Is there any other card that blocks this card?
    @property
    def is_blocked(self):
        return self.blocking_cards.exclude(list__type="done").exists()

    # Cards that are blocking this card and are not done
    @property
    def pending_blocking_cards(self):
        return self.blocking_cards.exclude(list__type="done")

    # Return the number of comments of a card
    @property
    def number_of_comments(self):
        return self.comments.all().count()

    # Returns the adjusted spent time according to the spent time factor defined in each member
    @property
    def adjusted_spent_time(self):
        adjusted_spent_time = 0
        for member in self.members.all():
            spent_time = self.daily_spent_times.filter(member=member).aggregate(sum=Sum("spent_time"))["sum"]
            if spent_time is not None:
                member_adjusted_spent_time = member.spent_time_factor * spent_time
                adjusted_spent_time += member_adjusted_spent_time

        return adjusted_spent_time

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
    def move(self, member, destination_list):
        if self.list.position < destination_list.position:
            movement_type = "forward"
        elif self.list.position > destination_list.position:
            movement_type = "backward"
        else:
            raise ValueError(u"Trying to move a card to its list")
        # Store the movement of this card
        card_movement = CardMovement(
            board=self.board, card=self, type=movement_type,
            source_list=self.list, destination_list=destination_list, datetime=timezone.now()
        )
        card_movement.save()
        # Move the card
        self.list = destination_list
        self.save()
        move_card(self, member, destination_list)

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
            self.spent_time += Decimal(spent_time)

        # Adding estimated time to the card
        if estimated_time is None:
            estimated_time = Decimal(spent_time)

        self.estimated_time += Decimal(estimated_time)

        # Updating the card
        self.save()

        # Creation of daily spent time
        DailySpentTime.add(self.board, member, date, self, description, spent_time, estimated_time)

        # Preparation of the comment content with the style of Plus for Trello
        days_ago_str = ""
        if days_ago:
            days_ago_str = "-{0}d ".format(days_ago)

        # Creation of comment with the daily spent time
        comment_content = Card.COMMENT_SPENT_ESTIMATED_TIME_PATTERN.format(
            days_ago=days_ago_str, spent_time=spent_time, estimated_time=estimated_time, description=description
        )

        self.add_comment(member, comment_content)

    # Add a new comment to this card
    @transaction.atomic
    def add_comment(self, member, content):
        # Add comment to Trello
        comment_data = add_comment_to_card(self, member, content)

        # Create comment locally using the id of the new comment in Trello
        card_comment = CardComment(uuid=comment_data["id"], card=self, author=member, content=content,
                                   creation_datetime=timezone.now())
        card_comment.save()


# Each one of the comments made by members in each card
class CardComment(ImmutableModel):

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
    card = models.ForeignKey("boards.Card", verbose_name=u"Card this commenb belongs to", related_name="comments")
    author = models.ForeignKey("members.Member", verbose_name=u"Member author of this comment", related_name="comments")
    content = models.TextField(verbose_name=u"Content of the comment")
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime of the comment")


# Label of the task board
class Label(ImmutableModel):

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
    uuid = models.CharField(max_length=128, verbose_name=u"External id of the list", unique=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="lists")
    type = models.CharField(max_length=64, choices=LIST_TYPE_CHOICES, default="before_development")
    position = models.PositiveIntegerField(verbose_name=u"Position of this list in the board", default=0)

    # Return all cards that are not archived (closed)
    @property
    def active_cards(self):
        return self.cards.filter(is_closed=False).order_by("position")

    @property
    def is_first(self):
        position_of_first_list = self.board.lists.aggregate(min_position=Min("position"))["min_position"]
        return self.position == position_of_first_list

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
