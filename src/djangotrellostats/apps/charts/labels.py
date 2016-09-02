# -*- coding: utf-8 -*-

import copy

import pygal
from django.db.models import Avg, Min
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
def avg_estimated_time_by_month(request, board=None):
    return avg_time_by_month(board, "estimated_time")


# Average estimated time by month
def avg_spent_time_by_month(request, board=None):
    return avg_time_by_month(board, "spent_time")


# Average spent/estimated time by month
def avg_time_by_month(board=None, time_measurement="spent_time"):
    daily_spent_time_filter = {"{0}__gt".format(time_measurement): 0}
    last_activity_date = timezone.now()
    if board:
        last_activity_date = board.last_activity_date
        daily_spent_time_filter["board"] = board

    chart_title = u"Task average {1} as of {0}".format(last_activity_date, time_measurement.replace("_", " "))
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    avg_spent_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                               print_zeroes=False,
                                               human_readable=True)
    labels = []
    if board:
        labels = board.labels.all()

    date_i = copy.deepcopy(
        DailySpentTime.objects.filter(**daily_spent_time_filter).aggregate(min_date=Min("date"))["min_date"]
    )
    if date_i is None:
        return avg_spent_time_chart.render_django_response()

    month_i = date_i.month
    year_i = date_i.year

    first_loop = True
    avg_time = None
    while first_loop or avg_time is not None:
        first_loop = False
        month_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).\
            filter(date__month=month_i, date__year=year_i)
        avg_time = month_spent_times.aggregate(avg_time=Avg(time_measurement))["avg_time"]
        if avg_time is not None:
            avg_spent_time_chart.add(u"{0}-{1}".format(year_i, month_i), avg_time)
            for label in labels:
                if label.name:
                    label_avg_time = month_spent_times.filters(labels=label).\
                                            aggregate(avg_time=Avg(time_measurement))["avg_time"]
                    if label_avg_time:
                        avg_spent_time_chart.add(u"{0} {1}-{2}".format(label.name, year_i, month_i), avg_time)

            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

    return avg_spent_time_chart.render_django_response()


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
