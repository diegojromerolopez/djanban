# -*- coding: utf-8 -*-

import copy
from datetime import datetime, time, timedelta
import pygal
import calendar
from datetime import date

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min, Q, Count
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board, Card
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.reports.models import ListReport, CardMovement


# Average card lead time
def avg_lead_time(request, board=None):
    chart_title = u"Task average lead time as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    lead_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False,
                                          human_readable=True)

    if not board:
        boards = get_user_boards(request.user)
        card_avg_lead_time = Card.objects.filter(board__in=boards).aggregate(Avg("lead_time"))["lead_time__avg"]
        lead_time_chart.add(u"All boards", card_avg_lead_time)
        if request.user.is_authenticated and hasattr(request.user, "member"):
            for board_i in boards:
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
        boards = get_user_boards(request.user)
        card_avg_cycle_time = Card.objects.filter(board__in=boards).aggregate(Avg("cycle_time"))["cycle_time__avg"]
        cycle_time_chart.add(u"All boards", card_avg_cycle_time)
        if request.user.is_authenticated and hasattr(request.user, "member"):
            for board_i in boards:
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
    chart_title = u"Average time of all task living in each list for board {0} as of {1}".format(board.name,
                                                                                                 board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    list_reports = ListReport.objects.filter(list__board=board)
    for list_report in list_reports:
        avg_time_by_list_chart.add(u"{0}".format(list_report.list.name), list_report.avg_card_time)

    return avg_time_by_list_chart.render_django_response()


# Cumulative list evolution by month
def cumulative_list_evolution(board, day_step=5):

    chart_title = u"Cumulative flow diagram as of {0}".format(timezone.now())
    chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=True,
                                  human_readable=True, x_label_rotation=45)

    start_working_date = board.get_working_start_date()
    if start_working_date is None:
        return cumulative_chart.render_django_response()

    end_working_date = board.get_working_end_date()
    if end_working_date is None:
        return cumulative_chart.render_django_response()

    # Y-Axis
    lists = board.lists.exclude(type="closed").order_by("position")
    list_values = {list_.id: [] for list_ in lists}

    x_labels = []

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))
        num_total_cards = 0
        for list_ in lists:
            list_id = list_.id
            # Number of cards that were created in this list before the date
            num_cards_without_movements = board.cards.filter(creation_datetime__lte=datetime_i, list=list_).\
                annotate(num_movements=Count("movements")).filter(num_movements=0).count()

            # Number of cards that were moved to this list before the date
            num_cards_moving_to_list = board.card_movements.filter(destination_list=list_,
                                                                   datetime__lte=datetime_i).count()

            num_cards = num_cards_moving_to_list + num_cards_without_movements
            num_total_cards += num_cards
            list_values[list_id].append(num_cards)

        if num_total_cards > 0:
            x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))
        date_i += timedelta(days=day_step)

    cumulative_chart.x_labels = x_labels
    for list_ in lists:
        list_id = list_.id
        cumulative_chart.add(list_.name, list_values[list_id])

    return cumulative_chart.render_django_response()

