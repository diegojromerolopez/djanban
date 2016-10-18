# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
import hashlib
import inspect
from datetime import timedelta

import pygal
from django.db.models import Min, Max, Sum
from django.utils import timezone
from django.template.defaultfilters import slugify

from djangotrellostats.apps.base.auth import get_user_boards, get_user_team_mates
from djangotrellostats.apps.charts.models import CachedChart
from djangotrellostats.apps.dev_environment.models import Interruption
from djangotrellostats.apps.members.models import Member


# Number of interruptions
def number_of_interruptions(current_user, board=None):
    chart_title = u"Number of interruptions as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, _interruption_count, incremental=False)


# Evolution of the number of interruptions
def evolution_of_interruptions(current_user, board=None):
    chart_title = u"Evolution of number of interruptions as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, _interruption_count, incremental=True)


# Interruption spent time
def interruption_spent_time(current_user, board=None):
    chart_title = u"Interruption spent time as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, _interruption_spent_time_sum, incremental=False)


# Evolution of the number of interruptions
def evolution_of_interruption_spent_time(current_user, board=None):
    chart_title = u"Evolution of interruption spent time as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, _interruption_spent_time_sum, incremental=True)


# Number of interruptions base function
def _number_of_interruptions(current_user, board, chart_title, interruption_measurement, incremental=False):

    # Caching
    chart_uuid = "interruptions.{0}".format(
        hashlib.sha256("_number_of_interruptions-{0}-{1}-{2}-{3}".format(
            current_user.id,
            board.id if board else "",
            inspect.getsource(interruption_measurement),
            "incremental" if incremental else "absolute"
        )).hexdigest()
    )
    try:
        chart = CachedChart.get(board=None, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    interruptions_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                     print_zeroes=False, x_label_rotation=65,
                                     human_readable=True)

    if incremental:
        datetime_filter = "datetime__date__lte"
        interruptions_chart.print_values = False
    else:
        datetime_filter = "datetime__date"

    interruptions_filter = {}
    if board:
        interruptions_filter["board"] = board
        boards = [board]
    else:
        boards = get_user_boards(current_user)
        interruptions_filter["member__in"] = get_user_team_mates(current_user)

    board_values = {board.id: [] for board in boards}

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")
    if not interruptions.exists():
        return interruptions_chart.render_django_response()

    min_datetime = interruptions.aggregate(min_datetime=Min("datetime"))["min_datetime"]
    max_datetime = interruptions.aggregate(max_datetime=Max("datetime"))["max_datetime"]

    date_i = copy.deepcopy(min_datetime.date())
    max_date = max_datetime.date() + timedelta(days=2)
    days = []
    num_interruptions = []
    while date_i <= max_date:
        interruptions_filter = {datetime_filter: date_i}
        interruptions_on_date = interruptions.filter(**interruptions_filter)
        interruptions_on_date_value = interruption_measurement(interruptions_on_date)

        # Add only values when there is some interruption in any project
        if interruptions_on_date_value > 0:
            days.append(date_i.strftime("%Y-%m-%d"))
            num_interruptions.append(interruptions_on_date_value)

            if board is None:
                for board_i in boards:
                    board_i_interruptions_value = interruption_measurement(interruptions_on_date.filter(board=board_i))
                    board_values[board_i.id].append(board_i_interruptions_value)

        date_i += timedelta(days=1)

    interruptions_chart.add(u"All interruptions", num_interruptions)
    for board_i in boards:
        if sum(board_values[board_i.id]) > 0:
            interruptions_chart.add(board_i.name, board_values[board_i.id])

    interruptions_chart.x_labels = days

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=interruptions_chart.render(is_unicode=True))
    return chart.render_django_response()


# Number of interruptions by member
def number_of_interruptions_by_member(current_user):
    chart_title = u"Number of interruptions by member as of {0}".format(timezone.now())
    return _number_of_interruptions_by_member(current_user, chart_title, _interruption_count, incremental=False)


# Evolution of the number of interruptions by member
def evolution_of_interruptions_by_member(current_user):
    chart_title = u"Evolution of number of interruptions by member as of {0}".format(timezone.now())
    return _number_of_interruptions_by_member(current_user, chart_title, _interruption_count, incremental=True)


# Spent time of interruptions by member
def interruption_spent_time_by_member(current_user):
    chart_title = u"Spent time on interruptions by member as of {0}".format(timezone.now())
    return _number_of_interruptions_by_member(current_user, chart_title, _interruption_spent_time_sum, incremental=False)


# Number of interruptions base function
def _number_of_interruptions_by_member(current_user, chart_title, interruption_measurement, incremental=False):
    chart_uuid = "interruptions._number_of_interruptions_by_member-{0}-{1}-{2}".format(
        current_user.id, slugify(chart_title), "incremental" if incremental else "absolute"
    )
    # Caching
    chart_uuid = "interruptions.{0}".format(
        hashlib.sha256("_number_of_interruptions_by_member-{0}-{1}-{2}".format(
            current_user.id,
            inspect.getsource(interruption_measurement),
            "incremental" if incremental else "absolute"
        )).hexdigest()
    )
    try:
        chart = CachedChart.get(board=None, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    interruptions_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                     print_zeroes=False, x_label_rotation=65,
                                     human_readable=True)

    if incremental:
        datetime_filter = "datetime__date__lte"
        interruptions_chart.print_values = False
    else:
        datetime_filter = "datetime__date"

    interruptions_filter = {}

    boards = get_user_boards(current_user)
    members = Member.objects.filter(boards__in=boards).distinct()
    member_values = {member.id: [] for member in members}
    interruptions_filter["member__in"] = members

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")
    if not interruptions.exists():
        return interruptions_chart.render_django_response()

    min_datetime = interruptions.aggregate(min_datetime=Min("datetime"))["min_datetime"]
    max_datetime = interruptions.aggregate(max_datetime=Max("datetime"))["max_datetime"]

    date_i = copy.deepcopy(min_datetime.date())
    max_date = max_datetime.date() + timedelta(days=2)
    days = []
    num_interruptions = []
    while date_i <= max_date:
        interruptions_filter = {datetime_filter: date_i}
        interruptions_on_date = interruptions.filter(**interruptions_filter)
        interruptions_on_date_value = interruption_measurement(interruptions_on_date)

        # Add only values when there is some interruption in any project
        if interruptions_on_date_value > 0:
            days.append(date_i.strftime("%Y-%m-%d"))
            num_interruptions.append(interruptions_on_date_value)

            for member_i in members:
                member_interruptions_on_date_value = interruption_measurement(interruptions_on_date.filter(member=member_i))
                member_values[member_i.id].append(member_interruptions_on_date_value)

        date_i += timedelta(days=1)

    interruptions_chart.add(u"All interruptions", num_interruptions)
    for member_i in members:
        if sum(member_values[member_i.id]) > 0:
            interruptions_chart.add(member_i.trello_username, member_values[member_i.id])

    interruptions_chart.x_labels = days

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=interruptions_chart.render(is_unicode=True))
    return chart.render_django_response()


# Number of interruptions by month
def number_of_interruptions_by_month(current_user, board=None):
    chart_title = u"Number of interruptions by month as of {0}".format(timezone.now())
    return _interruption_measurement_by_month(current_user, chart_title, _interruption_count, board)


# Spent time because of interruptions by month
def interruption_spent_time_by_month(current_user, board=None):
    chart_title = u"Interruption spent time by month as of {0}".format(timezone.now())
    return _interruption_measurement_by_month(current_user, chart_title, _interruption_spent_time_sum, board)


# Any measurement of interruptions by month
def _interruption_measurement_by_month(current_user, chart_title, interruption_measurement, board=None):

    chart_uuid = "interruptions.{0}".format(
        hashlib.sha256("_interruption_measurement_by_month-{0}-{1}-{2}".format(
            current_user.id,
            inspect.getsource(interruption_measurement),
            board.id if board else "None"
        )).hexdigest()
    )
    try:
        chart = CachedChart.get(board=None, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    interruptions_filter = {}
    if board:
        interruptions_filter["board"] = board
    else:
        interruptions_filter["member__in"] = get_user_team_mates(current_user)

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")

    interruptions_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                     print_zeroes=False, human_readable=True)

    min_datetime = interruptions.aggregate(min_datetime=Min("datetime"))["min_datetime"]
    max_datetime = interruptions.aggregate(max_datetime=Min("datetime"))["max_datetime"]
    if min_datetime is None or max_datetime is None:
        return interruptions_chart.render_django_response()

    datetime_i = copy.deepcopy(min_datetime)

    date_i = datetime_i.date()
    month_i = date_i.month
    year_i = date_i.year

    last_month = max_datetime.month
    last_year = max_datetime.year

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]

    months = []
    values = []
    board_values = {board.id: [] for board in boards}
    has_board_values = {board.id: False for board in boards }

    while year_i < last_year or year_i == last_year and month_i <= last_month:
        monthly_interruptions = interruptions.filter(datetime__month=month_i, datetime__year=year_i)
        monthly_measurement = interruption_measurement(monthly_interruptions)
        # For each month that have some data, add it to the chart
        if monthly_measurement > 0:
            months.append(u"{0}-{1}".format(year_i, month_i))
            values.append(monthly_measurement)
            for board in boards:
                monthly_interruption_measurement = interruption_measurement(monthly_interruptions.filter(board=board))
                board_values[board.id].append(monthly_interruption_measurement)
                if monthly_interruption_measurement > 0:
                    has_board_values[board.id] = True

        month_i += 1
        if month_i > 12:
            month_i = 1
            year_i += 1

    interruptions_chart.x_labels = months
    interruptions_chart.add(u"All interruptions", values)
    for board in boards:
        if has_board_values[board.id]:
            interruptions_chart.add(board.name, board_values[board.id])

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=interruptions_chart.render(is_unicode=True))
    return chart.render_django_response()


# Computes the sum of the spent time of a list of interruptions
def _interruption_spent_time_sum(interruptions_):
    sum_spent_time = interruptions_.aggregate(sum_spent_time=Sum("spent_time"))["sum_spent_time"]
    if sum_spent_time is None:
        return 0
    return sum_spent_time


# Count the number of interruptions
def _interruption_count(interruptions_):
    return interruptions_.count()