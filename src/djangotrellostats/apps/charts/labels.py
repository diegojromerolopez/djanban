# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy

import pygal
from django.db.models import Avg, Min, Count
from django.utils import timezone

from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.charts.models import CachedChart
from djangotrellostats.apps.dev_times.models import DailySpentTime



from djangotrellostats.apps.base.auth import user_is_member, user_is_visitor, get_user_boards
from datetime import date
from djangotrellostats.utils.week import number_of_weeks_of_year, get_iso_week_of_year


# Average spent times
def avg_spent_times(request, board=None):

    # Caching
    chart_uuid = "labels.avg_spent_times-{0}".format(board.id if board else "None")
    try:
        chart = CachedChart.get(board=board, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    chart_title = u"Average task spent time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False, human_readable=True)

    if board:
        cards = board.cards.all()
        avg_spent_time = cards.aggregate(Avg("spent_time"))["spent_time__avg"]
        avg_times_chart.add(u"Average spent time", avg_spent_time)
    else:
        boards = get_user_boards(request.user)
        cards = Card.objects.filter(board__in=boards)
        avg_spent_time = cards.aggregate(Avg("spent_time"))["spent_time__avg"]
        avg_times_chart.add(u"All boards", avg_spent_time)
        for board in boards:
            board_avg_spent_time = board.cards.aggregate(Avg("spent_time"))["spent_time__avg"]
            avg_times_chart.add(u"{0}".format(board.name), board_avg_spent_time)

    if board:
        labels = board.labels.all()

        for label in labels:
            if label.name:
                avg_times_chart.add(u"{0} average spent time".format(label.name), label.avg_spent_time())

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=avg_times_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average estimated times
def avg_estimated_times(request, board=None):

    # Caching
    chart_uuid = "labels.avg_estimated_times-{0}".format(board.id if board else "None")
    try:
        chart = CachedChart.get(board=board, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    chart_title = u"Average task estimated time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False, human_readable=True)

    if board:
        cards = board.cards.all()
        total_avg_estimated_time = cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
        avg_times_chart.add(u"Average estimated time", total_avg_estimated_time)
    else:
        boards = get_user_boards(request.user)
        cards = Card.objects.filter(board__in=boards)
        total_avg_estimated_time = cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
        avg_times_chart.add(u"All boards", total_avg_estimated_time)
        for board in boards:
            board_avg_estimated_time = board.cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
            avg_times_chart.add(u"{0}".format(board.name), board_avg_estimated_time)

    if board:
        labels = board.labels.all()

        for label in labels:
            if label.name:
                avg_times_chart.add(u"{0} average estimated time".format(label.name), label.avg_estimated_time())

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=avg_times_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average spent time by month
def avg_estimated_time_by_month(board=None):
    return _daily_spent_times_by_period(board, "estimated_time")


# Average estimated time by month
def avg_spent_time_by_month(board=None):
    return _daily_spent_times_by_period(board, "spent_time")


# Number of cards worked on by month
def number_of_cards_worked_on_by_month(board=None):
    return _daily_spent_times_by_period(board, "spent_time", operation="Count")


# Number of cards worked on by week
def number_of_cards_worked_on_by_week(board=None):
    return _daily_spent_times_by_period(board, "spent_time", operation="Count", period="week")


# Average spent/estimated time by week/month
def _daily_spent_times_by_period(board=None, time_measurement="spent_time", operation="Avg", period="month"):

    # Caching
    chart_uuid = "labels._daily_spent_times_by_period-{0}-{1}-{2}-{3}".format(board.id if board else "None", time_measurement, operation, period)
    try:
        chart = CachedChart.get(board=board, uuid=chart_uuid)
        return chart.render_django_response()
    except CachedChart.DoesNotExist:
        pass

    daily_spent_time_filter = {"{0}__gt".format(time_measurement): 0}
    last_activity_datetime = timezone.now()
    if board:
        last_activity_datetime = board.last_activity_datetime
        daily_spent_time_filter["board"] = board

    if operation == "Avg":
        chart_title = u"Task average {1} as of {0}".format(last_activity_datetime, time_measurement.replace("_", " "))
        if board:
            chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())
    elif operation == "Count":
        chart_title = u"Tasks worked on as of {0}".format(last_activity_datetime)
        if board:
            chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())
    else:
        ValueError(u"Operation not valid only Avg and Count values are valid")

    period_measurement_chart = pygal.StackedBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                print_zeroes=False,
                                                human_readable=True)
    labels = []
    if board:
        labels = board.labels.all()

    date_i = copy.deepcopy(
        DailySpentTime.objects.filter(**daily_spent_time_filter).aggregate(min_date=Min("date"))["min_date"]
    )
    if date_i is None:
        return period_measurement_chart.render_django_response()

    month_i = date_i.month
    week_i = get_iso_week_of_year(date_i)
    year_i = date_i.year

    if operation == "Avg":
        aggregation = Avg
    elif operation == "Count":
        aggregation = Count
    else:
        ValueError(u"Operation not valid only Avg and Count values are valid")

    measurement_titles = []
    measurement_values = []

    label_measurement_titles = {label.id: [] for label in labels}
    label_measurement_values = {label.id: [] for label in labels}

    first_loop = True
    period_measurement = None
    while first_loop or (period_measurement is not None and period_measurement > 0):
        if period == "month":
            period_filter = {"date__month": month_i, "date__year": year_i}
            measurement_title = u"{0}-{1}".format(year_i, month_i)
            label_measurement_title_suffix = u"{0}-{1}".format(year_i, month_i)
        elif period == "week":
            period_filter = {"week_of_year": week_i, "date__year": year_i}
            measurement_title = u"{0}W{1}".format(year_i, week_i)
            label_measurement_title_suffix = u"{0}W{1}".format(year_i, week_i)
        else:
            raise ValueError(u"Period {0} not valid. Only 'month' or 'week' is valid".format(period))

        first_loop = False
        month_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).\
            filter(**period_filter)
        period_measurement = month_spent_times.aggregate(measurement=aggregation(time_measurement))["measurement"]
        # For each month that have some data, add it to the chart
        if period_measurement is not None and period_measurement > 0:
            measurement_titles.append(measurement_title)
            measurement_values.append(period_measurement)

            # For each label that has a name (i.e. it is being used) and has a value, store its measurement per label
            for label in labels:
                if label.name:
                    label_measurement = month_spent_times.filter(card__labels=label).\
                                            aggregate(measurement=aggregation(time_measurement))["measurement"]
                    if label_measurement:
                        label_measurement_titles[label.id].append(measurement_title)
                        label_measurement_values[label.id].append(label_measurement)

            if period == "month":
                month_i += 1
                if month_i > 12:
                    month_i = 1
                    year_i += 1

            elif period == "week":
                week_i += 1
                if week_i > number_of_weeks_of_year(year_i):
                    week_i = 1
                    year_i += 1

    # Weeks there is any measurement
    period_measurement_chart.x_labels = measurement_titles
    period_measurement_chart.add("Tasks", measurement_values)

    # For each label that has any measurement, add its measurement to the chart
    for label in labels:
        if sum(label_measurement_values[label.id]) > 0:
            period_measurement_chart.add(label.name, label_measurement_values[label.id])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=period_measurement_chart.render(is_unicode=True))
    return chart.render_django_response()

