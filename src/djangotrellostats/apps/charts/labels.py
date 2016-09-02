# -*- coding: utf-8 -*-

import pygal
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone

from djangotrellostats.apps.boards.models import Card


# Average spent times
def avg_spent_times(request, board=None):
    chart_title = u"Average task spent as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False, human_readable=True)

    board = None
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


# Average estimated times
def avg_estimated_times(request, board=None):
    chart_title = u"Average task estimated time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False, human_readable=True)

    board = None
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
