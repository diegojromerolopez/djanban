# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from trello import TrelloClient

from djangotrellostats.apps.boards.models import Board, List
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
                                                 u"and other information", default=False)

    on_holidays = models.BooleanField(verbose_name=u"Is this developer on holidays?",
                                      help_text=u"If the developer is on holidays will stop receiving reports"
                                                u"and other emails", default=False)

    real_working_hours_per_week = models.PositiveIntegerField(u"Number of hours this developer should achieve each"
                                                              u"week", default=None, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)
        self.trello_client = self._get_trello_client()

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

    # Returns the number of hours this member has develop on a given date
    def get_spent_time(self, date, board=None):
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

    # Returns the number of hours this member has develop given a filter
    def _get_spent_time_sum_from_filter(self, spent_time_filter):
        spent_time_on_date = self.daily_spent_times.filter(**spent_time_filter). \
            aggregate(sum=Sum("spent_time"))["sum"]

        if spent_time_on_date is None:
            return 0
        return spent_time_on_date

    # Fetch basic information of boards and its lists
    @transaction.atomic
    def init_fetch(self, debug=False):
        trello_boards = self.trello_client.list_boards()
        for trello_board in trello_boards:
            board_already_exists = Board.objects.filter(uuid=trello_board.id).exists()
            if not board_already_exists:
                board_name = trello_board.name.decode("utf-8")
                board = Board(uuid=trello_board.id, name=board_name, last_activity_date=trello_board.date_last_activity,
                              creator=self)
                board.save()
                if debug:
                    print("Board {0} successfully created".format(board_name))

                # Fetch all lists of this board
                trello_lists = trello_board.all_lists()
                _lists = []
                for trello_list in trello_lists:
                    list_name = trello_list.name.decode("utf-8")
                    _list = List(uuid=trello_list.id, name=list_name, board=board)
                    if trello_list.closed:
                        _list.type = "closed"
                    _list.save()
                    _lists.append(_list)

                    if debug:
                        print("- List {1} of board {0} successfully created".format(board_name, list_name))

                # By default, consider the last list as "done" list
                last_list = _lists[-1]
                last_list.type = "done"
                last_list.save()

            else:
                board = Board.objects.get(uuid=trello_board.id)

            # Fetch all members this board and associate to this board
            self._fetch_members(board, trello_board)

    # Destroy boards created by this member
    def delete_current_data(self):
        self.created_boards.all().delete()

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
