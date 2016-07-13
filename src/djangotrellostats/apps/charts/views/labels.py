# -*- coding: utf-8 -*-

import pygal
from django.db.models import Avg
from djangotrellostats.apps.boards.models import Board, Card
from django.utils import timezone


# Average spent and estimated times
def avg_spent_times(request, board_id=None):
    chart_title = u"Average spent as of {0}".format(timezone.now())
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    board = None
    if board_id:
        board = Board.objects.get(id=board_id)
        cards = board.cards.all()
    else:
        cards = Card.objects.all()

    avg_spent_time = cards.aggregate(Avg("spent_time"))["spent_time__avg"]
    avg_times_chart.add(u"Average spent time", avg_spent_time)

    if board_id:
        labels = board.labels.all()

        for label in labels:
            avg_times_chart.add(u"{0} average spent time".format(label.name), label.avg_spent_time())

    return avg_times_chart.render_django_response()


# Average spent and estimated times
def avg_estimated_times(request, board_id=None):
    chart_title = u"Average estimated time as of {0}".format(timezone.now())
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    avg_times_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    board = None
    if board_id:
        board = Board.objects.get(id=board_id)
        cards = board.cards.all()
    else:
        cards = Card.objects.all()

    avg_estimated_time = cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
    avg_times_chart.add(u"Average estimated time", avg_estimated_time)

    if board_id:
        labels = board.labels.all()

        for label in labels:
            avg_times_chart.add(u"{0} average estimated time".format(label.name), label.avg_estimated_time())

    return avg_times_chart.render_django_response()
