# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from isoweek import Week


class Member(models.Model):
    api_key = models.CharField(max_length=128, verbose_name=u"Trello API key", null=True, default=None, blank=True)

    api_secret = models.CharField(max_length=128, verbose_name=u"Trello API secret", null=True, default=None, blank=True)

    token = models.CharField(max_length=128, verbose_name=u"Trello token", null=True, default=None, blank=True)

    token_secret = models.CharField(max_length=128, verbose_name=u"Trello token secret", null=True, default=None, blank=True)

    uuid = models.CharField(max_length=128, verbose_name=u"Trello member uuid", unique=True)

    trello_username = models.CharField(max_length=128, verbose_name=u"Trello username")

    initials = models.CharField(max_length=8, verbose_name=u"User initials in Trello")

    user = models.OneToOneField(User, verbose_name=u"Associated user", related_name="member", null=True, default=None)

    is_developer = models.BooleanField(verbose_name=u"Is this member a developer?",
                                       help_text=u"Informs if this member is a developer and hence will receive reports"
                                                 u" and other information", default=False)

    on_holidays = models.BooleanField(verbose_name=u"Is this developer on holidays?",
                                      help_text=u"If the developer is on holidays will stop receiving reports "
                                                u"and other emails", default=False)

    minimum_working_hours_per_day = models.PositiveIntegerField(
        verbose_name=u"Minimum number hours this developer should complete each day",
        default=None, null=True, blank=True)

    minimum_working_hours_per_week = models.PositiveIntegerField(
        verbose_name=u"Minimum number of hours this developer should complete per week",
        default=None, null=True, blank=True)

    spent_time_factor = models.DecimalField(
        decimal_places=2, max_digits=5,
        verbose_name=u"Factor that needs to be multiplied on the spent time price for this member",
        help_text=u"Modify this value whe this member cost8needs to be adjusted by a factor",
        default=1
    )

    # Constructor for Member
    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)

    # Resets the password of the associated user of this member
    def reset_password(self, new_password=None):
        # A member without an user cannot be his/her password changed
        if not self.user:
            raise ValueError(u"This member has not an associated user")
        # Create automatically a new password if None is passed
        if new_password is None:
            new_password = User.objects.make_random_password()
        # Setting up the new password
        self.user.set_password(new_password)
        self.user.save()
        return new_password

    # Informs if this member is initialized, that is, it has the credentials needed for connecting to trello.com
    def is_initialized(self):
        return self.api_key and self.api_secret and self.token and self.token_secret

    # Returns cards that belongs to this member and are currently under development
    def get_current_development_cards(self, board=None):
        development_cards = self.cards.filter(is_closed=False, list__type="development")
        # Filtering development cards by board
        if board:
            return development_cards.filter(board=board)
        return development_cards

    # Returns cards that are in development ordered by descending order according to when were worked on.
    def get_last_development_cards(self, board=None):
        development_cards = self.get_current_development_cards(board=board)
        return development_cards.order_by("-last_activity_datetime")

    # Returns the number of hours this member has develop today
    def get_today_spent_time(self, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")
        # We assume that we will not be working on holidays ever
        if self.on_holidays:
            return 0
        # Getting the spent time for today
        now = timezone.now()
        today = now.date()
        return self.get_spent_time(today, board)

    # Returns the number of hours this member developed yesterday
    def get_yesterday_spent_time(self, board=None):
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        return self.get_spent_time(yesterday, board)

    # Returns the number of hours this member has develop on a given date
    def get_spent_time(self, date, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")

        spent_time_on_date_filter = {"date": date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_date_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_date_filter)

    # Returns the number of hours this member has develop on a given week
    def get_weekly_spent_time(self, week, year, board=None):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_week_filter)

    # Returns the number of hours this member has develop on a given month
    def get_monthly_spent_time(self, month, year, board=None):
        spent_time_on_week_filter = {"date__month": month, "date__year": year}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_week_filter)

    # Returns the number of hours this member has develop given a filter
    def _get_spent_time_sum_from_filter(self, spent_time_filter):
        spent_time_on_date = self.daily_spent_times.filter(**spent_time_filter). \
            aggregate(sum=Sum("spent_time"))["sum"]

        if spent_time_on_date is None:
            return 0
        return spent_time_on_date

    # Destroy boards created by this member
    def delete_current_data(self):
        self.created_boards.all().delete()


