# -*- coding: utf-8 -*-

import pygal
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.utils import timezone

from djangotrellostats.apps.boards.models import Board, Card
from djangotrellostats.apps.reports.models import ListReport


# Average card lead time
def avg_lead_time(request, board=None):

    chart_title = u"Task average lead time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    lead_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False,
                                          human_readable=True)

    if not board:
        card_avg_lead_time = Card.objects.all().aggregate(Avg("lead_time"))["lead_time__avg"]
        lead_time_chart.add(u"All boards", card_avg_lead_time)
        if request.user.is_authenticated and hasattr(request.user, "member"):
            for board_i in request.user.member.boards.all():
                card_avg_lead_time = board_i.cards.all().aggregate(Avg("lead_time"))["lead_time__avg"]
                lead_time_chart.add(u"{0}".format(board_i.name), card_avg_lead_time)
    else:
        labels = board.labels.all()

        card_avg_lead_time = board.cards.all().aggregate(Avg("lead_time"))["lead_time__avg"]
        lead_time_chart.add(u"Card average lead time", card_avg_lead_time)

        for label in labels:
            if label.name:
                lead_time_chart.add(u"{0} average lead time".format(label.name), label.avg_lead_time())

    return lead_time_chart.render_django_response()


# Average card cycle time
def avg_cycle_time(request, board=None):
    chart_title = u"Task average cycle time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    cycle_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False,
                                           human_readable=True)

    if not board:
        card_avg_cycle_time = Card.objects.all().aggregate(Avg("cycle_time"))["cycle_time__avg"]
        cycle_time_chart.add(u"All boards", card_avg_cycle_time)
        if request.user.is_authenticated and hasattr(request.user, "member"):
            for board_i in request.user.member.boards.all():
                card_avg_cycle_time = board_i.cards.all().aggregate(Avg("cycle_time"))["cycle_time__avg"]
                cycle_time_chart.add(u"{0}".format(board_i.name), card_avg_cycle_time)

    else:
        labels = board.labels.all()

        card_avg_lead_time = board.cards.all().aggregate(Avg("cycle_time"))["cycle_time__avg"]
        cycle_time_chart.add(u"Task average cycle time", card_avg_lead_time)

        for label in labels:
            if label.name:
                cycle_time_chart.add(u"{0} average cycle time".format(label.name), label.avg_lead_time())

    return cycle_time_chart.render_django_response()


# Average card time in each list
def avg_time_by_list(board):
    chart_title = u"Average time of all task living in each list for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    list_reports = ListReport.objects.filter(list__board=board)
    for list_report in list_reports:
        avg_time_by_list_chart.add(u"{0}".format(list_report.list.name), list_report.avg_card_time)

    return avg_time_by_list_chart.render_django_response()
