# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
from datetime import timedelta

import pygal
from django.db.models import Min, Max, Sum
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.dev_environment.models import Interruption


# Number of interruptions
def number_of_interruptions(current_user, board=None):
    chart_title = u"Number of interruptions as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, incremental=False)


# Evolution of the number of interruptions
def evolution_of_interruptions(current_user, board=None):
    chart_title = u"Evolution of number of interruptions as of {0}".format(timezone.now())
    return _number_of_interruptions(current_user, board, chart_title, incremental=True)


# Number of interruptions base function
def _number_of_interruptions(current_user, board, chart_title, incremental=False):
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
        num_interruptions_on_date = interruptions_on_date.count()

        # Add only values when there is some interruption in any project
        if num_interruptions_on_date > 0:
            days.append(date_i.strftime("%Y-%m-%d"))
            num_interruptions.append(num_interruptions_on_date)

            if board is None:
                for board_i in boards:
                    board_i_num_interruptions = interruptions_on_date.filter(board=board_i).count()
                    board_values[board_i.id].append(board_i_num_interruptions)

        date_i += timedelta(days=1)

    interruptions_chart.add(u"Number of interruptions", num_interruptions)
    for board_i in boards:
        if sum(board_values[board_i.id]) > 0:
            interruptions_chart.add(board_i.name, board_values[board_i.id])

    interruptions_chart.x_labels = days

    return interruptions_chart.render_django_response()


# Number of interruptions by month
def number_of_interruptions_by_month(current_user, board=None):
    chart_title = u"Number of interruptions by month as of {0}".format(timezone.now())

    def interruption_measurement(interruptions):
        return interruptions.count()

    return _interruption_measurement_by_month(current_user, chart_title, interruption_measurement, board)


# Spent time because of interruptions by month
def interruption_spent_time_by_month(current_user, board=None):
    chart_title = u"Interruption spent time by month as of {0}".format(timezone.now())

    def interruption_measurement(interruptions):
        interruption_sum_spent_time = interruptions.aggregate(spent_time_sum=Sum("spent_time"))["spent_time_sum"]
        if interruption_sum_spent_time is None:
            return 0
        return interruption_sum_spent_time

    return _interruption_measurement_by_month(current_user, chart_title, interruption_measurement, board)


# Any measurement of interruptions by month
def _interruption_measurement_by_month(current_user, chart_title, interruption_measurement, board=None):
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    interruptions_filter = {}
    if board:
        interruptions_filter["board"] = board

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
    board_values = {board.id:[] for board in boards}
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

    return interruptions_chart.render_django_response()