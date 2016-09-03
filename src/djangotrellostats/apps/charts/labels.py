# -*- coding: utf-8 -*-

import copy

import pygal
from django.db.models import Avg, Min, Count
from django.utils import timezone

from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.dev_times.models import DailySpentTime


# Average spent times
def avg_spent_times(request, board=None):
    chart_title = u"Average task spent as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False, human_readable=True)

    if board:
        cards = board.cards.all()
        avg_spent_time = cards.aggregate(Avg("spent_time"))["spent_time__avg"]
        avg_times_chart.add(u"Average spent time", avg_spent_time)
    else:
        cards = Card.objects.all()
        avg_spent_time = cards.aggregate(Avg("spent_time"))["spent_time__avg"]
        avg_times_chart.add(u"All boards", avg_spent_time)
        for board in request.user.member.boards.all():
            board_avg_spent_time = board.cards.aggregate(Avg("spent_time"))["spent_time__avg"]
            avg_times_chart.add(u"{0}".format(board.name), board_avg_spent_time)

    if board:
        labels = board.labels.all()

        for label in labels:
            if label.name:
                avg_times_chart.add(u"{0} average spent time".format(label.name), label.avg_spent_time())

    return avg_times_chart.render_django_response()


# Average spent time by month
def avg_estimated_time_by_month(board=None):
    return _daily_spent_times_by_month(board, "estimated_time")


# Average estimated time by month
def avg_spent_time_by_month(board=None):
    return _daily_spent_times_by_month(board, "spent_time")


# Number of cards worked on by month
def number_of_cards_worked_on_by_month(board=None):
    return _daily_spent_times_by_month(board, "spent_time", operation="Count")


# Average spent/estimated time by month
def _daily_spent_times_by_month(board=None, time_measurement="spent_time", operation="Avg"):
    daily_spent_time_filter = {"{0}__gt".format(time_measurement): 0}
    last_activity_date = timezone.now()
    if board:
        last_activity_date = board.last_activity_date
        daily_spent_time_filter["board"] = board

    if operation == "Avg":
        chart_title = u"Task average {1} as of {0}".format(last_activity_date, time_measurement.replace("_", " "))
        if board:
            chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())
    elif operation == "Count":
        chart_title = u"Tasks worked on as of {0}".format(last_activity_date)
        if board:
            chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())
    else:
        ValueError(u"Operation not valid only Avg and Count values are valid")

    monthly_measurement_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                               print_zeroes=False,
                                               human_readable=True)
    labels = []
    if board:
        labels = board.labels.all()

    date_i = copy.deepcopy(
        DailySpentTime.objects.filter(**daily_spent_time_filter).aggregate(min_date=Min("date"))["min_date"]
    )
    if date_i is None:
        return monthly_measurement_chart.render_django_response()

    month_i = date_i.month
    year_i = date_i.year

    if operation == "Avg":
        aggregation = Avg
    elif operation == "Count":
        aggregation = Count
    else:
        ValueError(u"Operation not valid only Avg and Count values are valid")

    first_loop = True
    monthly_measurement = None
    while first_loop or (monthly_measurement is not None and monthly_measurement > 0):
        first_loop = False
        month_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).\
            filter(date__month=month_i, date__year=year_i)
        monthly_measurement = month_spent_times.aggregate(measurement=aggregation(time_measurement))["measurement"]
        # For each month that have some data, add it to the chart
        if monthly_measurement is not None and monthly_measurement > 0:
            monthly_measurement_chart.add(u"All tasks on {0}-{1}".format(year_i, month_i), monthly_measurement)
            for label in labels:
                if label.name:
                    label_measurement = month_spent_times.filters(labels=label).\
                                            aggregate(measurement=aggregation(time_measurement))["measurement"]
                    if label_measurement:
                        monthly_measurement_chart.add(u"{0} {1}-{2}".format(label.name, year_i, month_i), monthly_measurement)

            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

    return monthly_measurement_chart.render_django_response()


# Average estimated times
def avg_estimated_times(request, board=None):
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
        cards = Card.objects.all()
        total_avg_estimated_time = cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
        avg_times_chart.add(u"All boards", total_avg_estimated_time)
        for board in request.user.member.boards.all():
            board_avg_estimated_time = board.cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
            avg_times_chart.add(u"{0}".format(board.name), board_avg_estimated_time)

    if board:
        labels = board.labels.all()

        for label in labels:
            if label.name:
                avg_times_chart.add(u"{0} average estimated time".format(label.name), label.avg_estimated_time())

    return avg_times_chart.render_django_response()
