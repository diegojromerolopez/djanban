# -*- coding: utf-8 -*-
import copy

import pygal
from django.db.models import Sum, Avg
from django.utils import timezone

from djangotrellostats.apps.boards.models import MemberReport, Board, Card, ListReport
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member


def avg_lead_time(request, board_id=None):

    chart_title = u"Average lead time as of {0}".format(timezone.now())
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    lead_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    if not board_id:
        card_avg_lead_time = Card.objects.all().aggregate(Avg("lead_time"))["lead_time__avg"]
        lead_time_chart.add(u"Average lead time", card_avg_lead_time)

    else:
        board = Board.objects.get(id=board_id)
        labels = board.labels.all()

        card_avg_lead_time = board.cards.all().aggregate(Avg("lead_time"))["lead_time__avg"]
        lead_time_chart.add(u"Card average lead time", card_avg_lead_time)

        for label in labels:
            if label.name:
                lead_time_chart.add(u"{0} average lead time".format(label.name), label.avg_lead_time())

    return lead_time_chart.render_django_response()


def avg_cycle_time(request, board_id=None):
    chart_title = u"Average cycle time as of {0}".format(timezone.now())
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    cycle_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    if not board_id:
        card_avg_cycle_time = Card.objects.all().aggregate(Avg("cycle_time"))["cycle_time__avg"]
        cycle_time_chart.add(u"Average cycle time", card_avg_cycle_time)

    else:
        board = Board.objects.get(id=board_id)
        labels = board.labels.all()

        card_avg_lead_time = board.cards.all().aggregate(Avg("cycle_time"))["cycle_time__avg"]
        cycle_time_chart.add(u"Card average cycle time", card_avg_lead_time)

        for label in labels:
            if label.name:
                cycle_time_chart.add(u"{0} average cycle time".format(label.name), label.avg_lead_time())

    return cycle_time_chart.render_django_response()


def avg_time_by_list(request, board_id):
    board = Board.objects.get(id=board_id)
    chart_title = u"Average time all cards live in each list for board {0} as of ".format(board.name, board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    list_reports = ListReport.objects.filter(list__board=board)
    for list_report in list_reports:
        avg_time_by_list_chart.add(u"{0}".format(list_report.list.name), list_report.avg_card_time)

    return avg_time_by_list_chart.render_django_response()
