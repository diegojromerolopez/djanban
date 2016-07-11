# -*- coding: utf-8 -*-

import pygal
from django.db.models import Avg
from djangotrellostats.apps.boards.models import Fetch, Board, Card


# Average spent and estimated times
def avg_times(request, board_id=None):
    last_fetch = Fetch.last()

    chart_title = u"Average spent and estimated time as of {0}".format(last_fetch.get_human_creation_datetime())
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

    avg_estimated_time = cards.aggregate(Avg("estimated_time"))["estimated_time__avg"]
    avg_times_chart.add(u"Average estimated time", avg_estimated_time)

    if board_id:
        labels = board.labels.all()

        for label in labels:
            avg_times_chart.add(u"{0} average spent time".format(label.name), label.avg_spent_time())
            avg_times_chart.add(u"{0} average estimated time".format(label.name), label.avg_estimated_time())

    return avg_times_chart.render_django_response()