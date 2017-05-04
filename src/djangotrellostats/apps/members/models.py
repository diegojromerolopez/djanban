# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib
import os
from datetime import timedelta

import numpy
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.db.models import Sum, Avg, Q, Count
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.base.auth import get_user_boards, get_member_boards


class Member(models.Model):
    DEFAULT_MAX_NUMBER_OF_BOARDS = None

    creator = models.ForeignKey("members.Member", related_name="created_members", null=True, default=None, blank=True)

    user = models.OneToOneField(User, verbose_name=u"Associated user", related_name="member", null=True, default=None)

    default_avatar = models.ImageField(verbose_name=u"Default avatar", null=True, default=None)

    biography = models.TextField(verbose_name=u"Biography", blank=True, default="")

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

    max_number_of_boards = models.PositiveIntegerField(
        verbose_name=u"Max number of boards",
        help_text=u"Maximum number of boards this member can fetch. If null, unlimited number of boards",
        default=None, null=True
    )

    is_public = models.BooleanField(
        verbose_name=u"Is this member public?",
        help_text=u"If checked, this user will be seen by other members and they will be able to add it to their boards",
        default=False, blank=True
    )

    # Constructor for Member
    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)

    # Adjust spent time according to the factor specified by date intervals
    def adjust_daily_spent_time(self, daily_spent_time, attribute="spent_time", spent_time_factors=None):

        if spent_time_factors is None:
            spent_time_factors = self.spent_time_factors.all()

        return Member.adjust_daily_spent_time_from_spent_time_factors(
            daily_spent_time=daily_spent_time,
            spent_time_factors=spent_time_factors,
            attribute=attribute
        )

    # Adjust spent time according to the spent time factors passed as parameters
    @staticmethod
    def adjust_daily_spent_time_from_spent_time_factors(daily_spent_time, spent_time_factors, attribute="spent_time"):
        date = daily_spent_time.date
        adjusted_value = getattr(daily_spent_time, attribute)
        if adjusted_value is None:
            return 0

        for spent_time_factor in spent_time_factors:
            if (spent_time_factor.start_date is None and spent_time_factor.end_date is None) or\
                    (spent_time_factor.start_date <= date and spent_time_factor.end_date is None) or \
                    (spent_time_factor.start_date <= date <= spent_time_factor.end_date):
                original_value = getattr(daily_spent_time, attribute)
                adjusted_value = original_value * spent_time_factor.factor
                #print "{0} {1} * {2} = {3}".format(self.external_username, original_value, spent_time_factor.factor, adjusted_value)
                return adjusted_value

        return adjusted_value

    # A native member is one that has no Trello profile
    @property
    def is_native(self):
        return not self.has_trello_profile

    # Inform if this member was fetched from Trello (alias method).
    @property
    def has_trello_profile(self):
        return hasattr(self, "trello_member_profile") and self.trello_member_profile

    # Inform if this member was fetched from Trello
    @property
    def has_trello_member_profile(self):
        return self.has_trello_profile

    # Has this uses credentials to make actions with the Trello API?
    @property
    def has_trello_credentials(self):
        return self.has_trello_profile and self.trello_member_profile.is_initialized

    @property
    def uuid(self):
        if self.has_trello_profile:
            return self.trello_member_profile.trello_id
        return self.id

    # Alias very useful for now
    @property
    def external_username(self):
        if self.has_trello_profile:
            return self.trello_member_profile.username
        if self.user:
            return self.user.username
        return "Member {0}".format(self.id)

    @property
    def initials(self):
        if self.has_trello_profile:
            return self.trello_member_profile.initials
        if self.user:
            return self.user.username
        return "Member {0}".format(self.id)

    # Return the members this member can see. That is:
    # - Members of one of his/her boards.
    # - Members created by this member.
    # - Public members.
    @property
    def viewable_members(self):
        boards = []
        if self.user:
            boards = get_user_boards(self.user)
        return Member.objects.filter(Q(boards__in=boards) | Q(creator=self) | Q(is_public=True)).distinct()

    # Get member companions of the same boards
    @property
    def team_mates(self):
        return Member.get_user_team_mates(self.user)

    # Get members that work with this user
    @staticmethod
    def get_user_team_mates(user):
        boards = get_user_boards(user)
        return Member.objects.filter(boards__in=boards).distinct().order_by("id")

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

    # Returns cards that belongs to this member and are currently under development
    def get_current_development_cards(self, board=None):
        development_cards = self.cards.filter(board__is_archived=False, is_closed=False, list__type="development")
        # Filtering development cards by board
        if board:
            return development_cards.filter(board=board)
        return development_cards

    # Returns cards that are in development ordered by descending order according to when were worked on.
    def get_last_development_cards(self, board=None):
        development_cards = self.get_current_development_cards(board=board)
        return development_cards.order_by("-last_activity_datetime")

    # Return the last notifications (10 by default)
    def get_last_unread_notifications(self, number=10):
        return self.received_notifications.filter(is_read=False).order_by("-creation_datetime")[:number]

    # Returns the number of hours this member has develop today
    def get_today_spent_time(self, board=None):
        # Getting the spent time for today
        now = timezone.now()
        today = now.date()
        return self.get_spent_time(today, board)

    # Returns the number of hours this member has develop today
    def get_today_adjusted_spent_time(self, board=None):
        # Getting the adjusted spent time for today
        now = timezone.now()
        today = now.date()
        return self.get_adjusted_spent_time(today, board)

    # Returns the number of hours this member developed yesterday
    def get_yesterday_spent_time(self, board=None):
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        return self.get_spent_time(yesterday, board)

    # Returns the number of adjusted hours this member developed yesterday
    def get_yesterday_adjusted_spent_time(self, board=None):
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        return self.get_adjusted_spent_time(yesterday, board)

    # Returns the number of hours this member has develop on a given date
    def get_spent_time(self, date, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")

        spent_time_on_date_filter = {"date": date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_date_filter["board"] = board

        return self._sum_spent_time_from_filter(spent_time_on_date_filter)

    # Returns the number of adjusted hours this member has develop on a given date
    def get_adjusted_spent_time(self, date, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")

        spent_time_on_date_filter = {"date": date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_date_filter["board"] = board

        return self._sum_adjusted_spent_time_from_filter(spent_time_on_date_filter)

    # Returns the number of hours this member has develop on a given week
    def get_weekly_spent_time(self, week, year, board=None):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._sum_spent_time_from_filter(spent_time_on_week_filter)

    # Returns the number of adjusted hours this member has develop on a given week
    def get_weekly_adjusted_spent_time(self, week, year, board=None):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._sum_adjusted_spent_time_from_filter(spent_time_on_week_filter)

    # Returns the number of hours this member has develop on a given month
    def get_monthly_spent_time(self, month, year, board=None):
        spent_time_on_month_filter = {"date__month": month, "date__year": year}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_month_filter["board"] = board

        return self._sum_spent_time_from_filter(spent_time_on_month_filter)

    # Returns the number of adjusted hours this member has develop on a given month
    def get_monthly_adjusted_spent_time(self, month, year, board=None):
        spent_time_on_month_filter = {"date__month": month, "date__year": year}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_month_filter["board"] = board

        return self._sum_adjusted_spent_time_from_filter(spent_time_on_month_filter)

    # Returns the sum of this member's number of spent time for the daily spent filter passed as parameter
    def _sum_spent_time_from_filter(self, daily_spent_time_filter):
        daily_spent_times = self.daily_spent_times.filter(**daily_spent_time_filter)
        return Member._sum_spent_time(daily_spent_times)

    # Returns the sum of this member's number of adjusted spent time for the daily spent filter passed as parameter
    def _sum_adjusted_spent_time_from_filter(self, daily_spent_time_filter):
        daily_spent_times = self.daily_spent_times.filter(**daily_spent_time_filter)
        spent_time_factors = self.spent_time_factors.all()
        adjusted_spent_time_sum = 0
        for daily_spent_time in daily_spent_times:
            adjusted_spent_time_sum += self.adjust_daily_spent_time(
                daily_spent_time, attribute="spent_time", spent_time_factors=spent_time_factors
            )
        return adjusted_spent_time_sum

    # Returns the number of hours this member has develop given a filter
    @staticmethod
    def _sum_spent_time(daily_spent_times):
        spent_time = daily_spent_times. \
            aggregate(sum=Sum("spent_time"))["sum"]
        if spent_time is None:
            return 0
        return spent_time

    # Destroy boards created by this member
    def delete_current_data(self):
        self.created_boards.all().delete()

    # Mood of this member
    @property
    def mood(self):
        happy_days = self.daily_member_moods.filter(mood="happy").count()
        normal_days = self.daily_member_moods.filter(mood="normal").count()
        sad_days = self.daily_member_moods.filter(mood="sad").count()
        all_days = (happy_days + normal_days + sad_days)
        if all_days == 0:
            return 0.0
        return 1.0 * (happy_days - sad_days) / all_days

    def get_role(self, board):
        try:
            return self.roles.get(board=board)
        except MemberRole.DoesNotExist:
            member_role, created = MemberRole.objects.get_or_create(type="normal", board=board)
            member_role.members.add(self)
        return member_role

    @property
    def active_cards(self):
        return self.cards.filter(board__is_archived=False, is_closed=False).order_by("position")

    def all_boards_in_downtime(self):
        resumed_boards = get_member_boards(self).\
            annotate(num_resumed_cards=Count(
                    models.Case(
                        models.When(cards__is_closed=False, cards__list__type="development",  then=1),
                        models.When(cards__is_closed=False, cards__list__type="ready_to_develop",  then=1),
                        default=0,
                        output_field=models.IntegerField()
                    ))
            ).\
            filter(num_resumed_cards__gt=0)
        return not resumed_boards.exists()

    # Is the member in downtime?
    @property
    def is_in_downtime(self):
        return not self.active_cards.filter(Q(list__type="development")|Q(list__type="ready_to_develop")).exists()

    @property
    def first_work_datetime(self):
        try:
            return self.daily_spent_times.all().order_by("id")[0].comment.creation_datetime
        except (IndexError, AttributeError):
            return None

    @property
    def last_work_datetime(self):
        try:
            return self.daily_spent_times.all().order_by("-id")[0].comment.creation_datetime
        except (IndexError, AttributeError):
            return None

    @property
    def number_of_cards(self):
        return self.active_cards.count()

    @property
    def forward_movements(self):
        return self.card_movements.filter(type="forward").count()

    @property
    def backward_movements(self):
        return self.card_movements.filter(type="backward").count()

    def get_forward_movements_for_board(self, board):
        return self.card_movements.filter(type="forward", board=board).count()

    def get_backward_movements_for_board(self, board):
        return self.card_movements.filter(type="backward", board=board).count()

    # Returns the Gravatar URL
    @property
    def gravatar_url(self, size=30):
        # Create avatar if it doesn't exist
        if not self.default_avatar:
            self.create_default_avatar()
        # If the member has an user and therefore, an email, get its gravatar
        if self.user:
            return "http://www.gravatar.com/avatar/{0}?s={1}&d={2}".format(
                hashlib.md5(self.user.email.encode('utf-8')).hexdigest(),
                size,
                self.default_avatar.url
            )
        # Otherwise, get its default avatar URL
        return self.default_avatar.url

    # Create default avatar
    def create_default_avatar(self):

        initials = self.initials

        font = ImageFont.truetype(settings.BASE_DIR + "/fonts/vera.ttf", size=15)

        canvas = Image.new('RGB', (30, 30), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        draw.text((4, 8), initials, (0, 0, 0), font=font)

        filename = "{0}.png".format(initials)
        path = os.path.join(settings.TMP_DIR, "{0}".format(filename))

        canvas.save(path, "PNG")

        with open(path, "rb") as avatar_image:
            self.default_avatar.save(filename, File(avatar_image))

    # Average lead time of the cards of this member
    @property
    def avg_card_lead_time(self):
        return self.active_cards.aggregate(avg=Avg("lead_time"))["avg"]

    # Average spent time of the cards of this member
    @property
    def avg_card_spent_time(self):
        return self.active_cards.aggregate(avg=Avg("spent_time"))["avg"]

    # Average estimated time of the cards of this member
    @property
    def avg_card_estimated_time(self):
        return self.active_cards.aggregate(avg=Avg("estimated_time"))["avg"]

    # Standard deviation of the lead time of the cards of this member
    @property
    def std_dev_card_lead_time(self):
        values = [float(card_i.lead_time) for card_i in self.active_cards.exclude(lead_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time

    # Standard deviation of the spent time of the cards of this member
    @property
    def std_dev_card_spent_time(self):
        values = [float(card_i.spent_time) for card_i in self.active_cards.exclude(spent_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time

    # Standard deviation of the estimated time of the cards of this member
    @property
    def std_dev_card_estimated_time(self):
        values = [float(card_i.estimated_time) for card_i in self.active_cards.exclude(estimated_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time

    @property
    def first_name(self):
        if self.user:
            return self.user.first_name
        return None

    @property
    def last_name(self):
        if self.user:
            return self.user.last_name
        return None

    @property
    def email(self):
        if self.user:
            return self.user.email
        return None


# Spent factors of each member
class SpentTimeFactor(models.Model):
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="spent_time_factors")
    name = models.CharField(verbose_name=u"Name of this factor", max_length=128, default="", blank=True)
    start_date = models.DateField(verbose_name=u"Start date of this factor")
    end_date = models.DateField(verbose_name=u"End date of this factor", null=True, default=None, blank=True)
    factor = models.DecimalField(
        decimal_places=2, max_digits=5,
        verbose_name=u"Factor that needs to be multiplied on the spent time price for this member",
        help_text=u"Modify this value whe this member cost needs to be adjusted by a factor",
        default=1
    )


# Role a member has in a board
class MemberRole(models.Model):
    TYPE_CHOICES = (
        ("admin", "Administrator"),
        ("normal", "Normal"),
        ("guest", "Guest")
    )
    type = models.CharField(verbose_name="Role a member has in a board", default="normal", max_length=32)
    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="roles")
    board = models.ForeignKey("boards.Board", verbose_name=u"Boards", related_name="roles")

    # Return the full name of the type
    @property
    def name(self):
        return dict(MemberRole.TYPE_CHOICES)[self.type]


#
class TrelloMemberProfile(models.Model):

    api_key = models.CharField(max_length=128, verbose_name=u"Trello API key", null=True, default=None, blank=True)

    api_secret = models.CharField(max_length=128,
                                  verbose_name=u"Trello API secret (obsolete)",
                                  help_text=u"Trello API secret. Deprecated and not used. This field will be removed.",
                                  null=True, default=None, blank=True)

    token = models.CharField(max_length=128, verbose_name=u"Trello token", null=True, default=None, blank=True)

    token_secret = models.CharField(max_length=128, verbose_name=u"Trello token secret", null=True, default=None, blank=True)

    trello_id = models.CharField(max_length=128, verbose_name=u"Trello member id", unique=True)

    username = models.CharField(max_length=128, verbose_name=u"Trello username")

    initials = models.CharField(max_length=8, verbose_name=u"User initials in Trello")

    member = models.OneToOneField(Member, verbose_name=u"Associated member", related_name="trello_member_profile", null=True, default=None)

    # Informs if this member is initialized, that is, it has the credentials needed for connecting to trello.com
    @property
    def is_initialized(self):
        return self.api_key and self.api_secret and self.token and self.token_secret

    @property
    def user(self):
        if self.member:
            return self.member.user
        return None