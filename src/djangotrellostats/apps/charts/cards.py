# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import math
import numpy
import copy
import inspect
from datetime import datetime, time, timedelta
import pygal
import calendar
from datetime import date

import pytz
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min, Q, Count, Max, Sum
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board, Card, CardComment, Label, List
from djangotrellostats.apps.charts.models import CachedChart
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.reports.models import CardMovement


# Average card lead time
def avg_lead_time(request, board=None):

    # Caching
    chart_uuid = "cards.avg_lead_time-{0}".format(board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

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

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=lead_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average card cycle time
def avg_cycle_time(request, board=None):

    # Caching
    chart_uuid = "cards.avg_cycle_time-{0}".format(board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

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

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=cycle_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average card lead time by month
def avg_lead_time_by_month(request, board=None):
    return _avg_metric_time_by_month(request, board=board, metric="lead")


# Average card cycle time by month
def avg_cycle_time_by_month(request, board=None):
    return _avg_metric_time_by_month(request, board=board, metric="cycle")


# Average card metric (lead/cycle) by month
def _avg_metric_time_by_month(request, board=None, metric="lead"):
    # The metric is only lead or cycle
    if metric != "lead" and metric != "cycle" and metric != "spent_time" and metric != "estimated_time":
        raise ValueError("The metric must be 'lead' or 'cycle'")

    # Caching
    chart_uuid = "cards._avg_metric_time_by_month-{0}-{1}".format(board.id if board else "None", metric)
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Task average {0} time by month as of {1}".format(metric, timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    metric_time_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                   print_zeroes=False, human_readable=True)

    if board is None:
        boards = get_user_boards(request.user)
        labels = None
    else:
        boards = [board]
        labels = board.labels.exclude(name="").order_by("name")

    # Getting the time limits of our chart
    start_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(min_date=Min("date"))["min_date"]
    end_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(max_date=Max("date"))["max_date"]
    if start_working_date is None or end_working_date is None:
        return metric_time_chart.render_django_response()

    last_month = end_working_date.month
    last_year = end_working_date.year

    cards = Card.objects.filter(board__in=boards)

    x_labels = []
    metric_time_values = []
    if board:
        for label in labels:
            label.metric_values = []

    # Passing through the months getting the cards that were worked on by last time in that month and year
    month_i = copy.deepcopy(start_working_date.month)
    year_i = start_working_date.year
    while year_i < last_year or year_i == last_year and month_i <= last_month:
        cards_ending_this_month = cards.filter(list__type="done",
                                               last_activity_datetime__month=month_i,
                                               last_activity_datetime__year=year_i,
                                               movements__destination_list__type="done")

        if cards_ending_this_month.exists():
            x_labels.append(u"{0}-{1}".format(year_i, month_i))
            if metric == "lead":
                def card_metric(card_):
                    return card_.lead_time
            elif metric == "cycle":
                def card_metric(card_):
                    return card_.cycle_time
            elif metric == "spent_time":
                def card_metric(card_):
                    if card_.spent_time is None:
                        return 0
                    return card_.spent_time
            elif metric == "estimated_time":
                def card_metric(card_):
                    if card_.estimated_time is None:
                        return 0
                    return card_.estimated_time

            else:
                raise ValueError("The metric must be 'lead' or 'cycle'")

            card_metric_value = filter(lambda v: v is not None, [card_metric(card) for card in cards_ending_this_month])
            if len(card_metric_value) > 0:
                metric_time_values.append(numpy.mean(card_metric_value))
                if board:
                    for label in labels:
                        label_cards = cards_ending_this_month.filter(labels=label)
                        if label_cards.exists():
                            label_metric_value = [card_metric(card) for card in label_cards]
                            label.metric_values.append(numpy.mean(filter(lambda v: v is not None, label_metric_value)))

        month_i += 1
        if month_i > 12:
            month_i = 1
            year_i += 1

    metric_time_chart.x_labels = x_labels
    metric_name = metric[0].upper() + metric[1:]
    metric_title = "{0} time for all cards".format(metric_name)
    metric_time_chart.add(metric_title, metric_time_values)

    if board:
        for label in labels:
            metric_time_chart.add("{1} cards".format(metric_name, label.name), label.metric_values)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=metric_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average card time in each list
def avg_time_by_list(board, workflow=None):
    # Caching
    chart_uuid = "cards.avg_time_by_list-{0}-{1}".format(board.id, workflow.id if workflow else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Average time of all tasks living in each list for board {0} ".format(board.name)
    if workflow:
        chart_title += "for workflow {0} ".format(workflow.name)

    chart_title += "as of {0}".format(board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    lists = board.active_lists.all()
    if workflow:
        lists = workflow.lists.all()
    for list_ in lists:
        avg_time_by_list_chart.add(u"{0}".format(list_.name), list_.avg_card_time_in_list)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=avg_time_by_list_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average card estimated time in each list
def avg_std_dev_time_by_list(board, workflow=None):
    # Caching
    chart_uuid = "cards.avg_std_dev_time_by_list-{0}-{1}".format(board.id, workflow.id if workflow else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Average standard deviation time of all tasks living in each list for board {0} ".format(board.name)
    if workflow:
        chart_title += "for workflow {0} ".format(workflow.name)

    chart_title += "as of {0}".format(board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    lists = board.active_lists.all()
    if workflow:
        lists = workflow.lists.all()
    for list_ in lists:
        avg_time_by_list_chart.add(u"{0}".format(list_.name), list_.std_dev_card_time_in_list)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=avg_time_by_list_chart.render(is_unicode=True))
    return chart.render_django_response()


# List evolution by month
def absolute_flow_diagram(board, day_step=1):

    # Caching
    chart_uuid = "cards.absolute_flow_diagram-{0}-{1}".format(board.id, day_step)
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Flow diagram as of {0}".format(timezone.now())
    chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=False,
                                  x_labels_major_every=3, show_only_major_dots=True,
                                  show_minor_x_labels=False,
                                  human_readable=True, x_label_rotation=65)

    start_working_date = board.get_working_start_date()
    end_working_date = board.get_working_end_date()
    if start_working_date is None or end_working_date is None:
        return cumulative_chart.render_django_response()

    # Y-Axis
    lists = board.lists.exclude(type="closed").order_by("position")
    list_values = {list_.id: [] for list_ in lists}

    x_labels = []

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))
        for list_ in lists:
            list_id = list_.id
            # Number of cards that were created in this list before the date
            num_cards_without_movements = board.cards.filter(creation_datetime__lt=datetime_i,
                                                             creation_datetime__gte=datetime_i-timedelta(days=day_step),
                                                             list=list_). \
                annotate(num_movements=Count("movements")).filter(num_movements=0).count()

            # Number of cards that were moved to this list before the date
            num_cards_moving_to_list = board.card_movements.filter(
                destination_list=list_,
                datetime__lt=datetime_i,
                datetime__gte=datetime_i-timedelta(days=day_step),
            ).count()

            num_cards = num_cards_moving_to_list + num_cards_without_movements
            list_values[list_id].append(num_cards)

        x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))

        date_i += timedelta(days=day_step)

    cumulative_chart.x_labels = x_labels
    for list_ in lists:
        list_id = list_.id
        cumulative_chart.add(list_.name, list_values[list_id])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=cumulative_chart.render(is_unicode=True))
    return chart.render_django_response()


# Cumulative list evolution by month
def cumulative_flow_diagram(board, day_step=1):

    # Caching
    chart_uuid = "cards.cumulative_flow-diagram-{0}-{1}".format(board.id, day_step)
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Cumulative flow diagram as of {0}".format(timezone.now())
    chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=True,
                                  x_labels_major_every=3, show_only_major_dots=True,
                                  show_minor_x_labels=False,
                                  human_readable=True, x_label_rotation=65)

    # If there are no cards, return the empty chart
    if not board.active_cards.all().exists():
        return cumulative_chart.render_django_response()

    start_working_date = board.get_working_start_date()
    end_working_date = board.get_working_end_date()
    if start_working_date is None or end_working_date is None:
        return cumulative_chart.render_django_response()

    # Y-Axis
    lists = board.lists.exclude(type="closed").order_by("position")
    list_values = {list_.id: [] for list_ in lists}

    x_labels = []

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))
        for list_ in lists:
            list_id = list_.id
            # Number of cards that were created in this list before the date
            num_cards_without_movements = board.cards.filter(creation_datetime__lte=datetime_i, list=list_). \
                annotate(num_movements=Count("movements")).filter(num_movements=0).count()

            # Number of cards that were moved to this list before the date
            num_cards_moving_to_list = board.card_movements.filter(
                destination_list__position__gte=list_.position,
                datetime__lt=datetime_i,
            ).count()

            num_cards = num_cards_moving_to_list + num_cards_without_movements
            list_values[list_id].append(num_cards)

        x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))
        date_i += timedelta(days=day_step)

    cumulative_chart.x_labels = x_labels
    for list_ in lists:
        list_id = list_.id
        cumulative_chart.add(list_.name, list_values[list_id])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=cumulative_chart.render(is_unicode=True))
    return chart.render_django_response()


# Cumulative list type evolution by month
def cumulative_list_type_evolution(current_user, board=None, day_step=1):

    # Caching
    if board:
        chart_uuid = "cards.cumulative_list_type_evolution-{0}-{1}".format(board.id, day_step)
    else:
        chart_uuid = "cards.cumulative_list_type_evolution-all-{0}".format(day_step)

    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Cumulative flow diagram as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=True,
                                  x_labels_major_every=7, show_only_major_dots=True,
                                  show_minor_x_labels=False,
                                  human_readable=True, x_label_rotation=65)

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    if Card.objects.filter(board__in=boards).exists():
        return cumulative_chart.render_django_response()

    start_working_date = numpy.min(filter(None, [board_i.get_working_start_date() for board_i in boards]))
    end_working_date = numpy.max(filter(None, [board_i.get_working_end_date() for board_i in boards]))
    if start_working_date is None or end_working_date is None:
        return cumulative_chart.render_django_response()

    # Y-Axis
    list_type_values = {list_type: [] for list_type in List.LIST_TYPES}

    # Cards of current user boards
    cards = Card.objects.filter(board__in=boards)

    # Card movements of current user boards
    card_movements = CardMovement.objects.filter(board__in=boards)

    x_labels = []

    num_list_types = len(List.LIST_TYPES)

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))
        num_total_cards = 0
        for list_type_index in range(0, num_list_types):
            list_type = List.LIST_TYPES[list_type_index]

            # Number of cards that were created in this list before the date
            num_cards_without_movements = cards.filter(creation_datetime__lte=datetime_i, list__type=list_type)\
                .filter(number_of_forward_movements=0, number_of_backward_movements=0).count()

            # Number of cards that were moved to this list before the date
            num_cards_moving_to_list = card_movements.filter(
                destination_list__type__in=List.LIST_TYPES[list_type_index:],
                datetime__lte=datetime_i
            ).count()

            num_cards = num_cards_moving_to_list + num_cards_without_movements
            num_total_cards += num_cards
            list_type_values[list_type].append(num_cards)

        if num_total_cards > 0:
            x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))

        date_i += timedelta(days=day_step)

    cumulative_chart.x_labels = x_labels
    list_types_dict = dict(List.LIST_TYPE_CHOICES)
    for list_type in List.LIST_TYPES:
        list_type_name = list_types_dict[list_type]
        cumulative_chart.add(list_type_name, list_type_values[list_type])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=cumulative_chart.render(is_unicode=True))
    return chart.render_django_response()


# Cards-in cards-out
# Number of cards that are created vs number of cards that are completed along the live of the project
def cumulative_card_evolution(current_user, board=None, day_step=1):

    # Caching
    if board:
        chart_uuid = "cards.cumulative_card_evolution-{0}-{1}".format(board.id, day_step)
    else:
        chart_uuid = "cards.cumulative_card_evolution-all-{0}".format(day_step)

    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    chart_title = u"Number of created cards vs completed cards as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=False,
                                  x_labels_major_every=3, show_only_major_dots=True,
                                  show_minor_x_labels=False,
                                  human_readable=True, x_label_rotation=65)

    cumulative_chart.x_labels_major_every = 7
    cumulative_chart.show_only_major_dots = True

    # If there are no cards, return the empty chart
    if not Card.objects.filter(board__in=boards).exists():
        return cumulative_chart.render_django_response()

    # If there have no been work, return the empty chart
    start_working_date = numpy.min(filter(None, [board_i.get_working_start_date() for board_i in boards]))
    end_working_date = numpy.max(filter(None, [board_i.get_working_end_date() for board_i in boards]))
    if start_working_date is None or end_working_date is None:
        return cumulative_chart.render_django_response()

    # Labels of the board
    if board:
        labels = board.labels.exclude(name="").order_by("name")
    else:
        labels = Label.objects.exclude(name="").filter(board__in=boards).order_by("name")

    # Number of created cards by label
    created_card_values_by_label = {label.id: [] for label in labels}

    # Number of done cards by label
    done_card_values_by_label = {label.id: [] for label in labels}

    num_created_card_values = []
    num_done_card_values = []

    x_labels = []

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        #print "{0} <= {1}".format(date_i, end_working_date)
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))

        # Created cards that were created in this list before the date
        created_cards = Card.objects.filter(creation_datetime__lte=datetime_i, board__in=boards)

        # Number of created cards that were created in this list before the date
        num_created_cards = created_cards.count()

        # Cards that were moved to this list before the date
        done_cards = CardMovement.objects.filter(board__in=boards,
                                                 destination_list__type="done",
                                                 datetime__lte=datetime_i)

        # Number of cards that were moved to this list before the date
        num_done_cards = done_cards.count()

        # When there has been created or terminated any card
        if num_created_cards > 0 or num_done_cards > 0:
            num_created_card_values.append(num_created_cards)
            num_done_card_values.append(num_done_cards)

            x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))

            # Each category filtered by label
            if board:
                for label in labels:
                    # Number of created cards with this label (considered only if there are any)
                    num_created_cards_with_this_label = label.cards.filter(id__in=created_cards).count()
                    if num_created_cards_with_this_label == 0:
                        num_created_cards_with_this_label = None
                    created_card_values_by_label[label.id].append(num_created_cards_with_this_label)

                    # Number of done cards with this label (considered only if there are any)
                    num_done_cards_with_this_label = label.cards.filter(id__in=done_cards).count()
                    if num_done_card_values == 0:
                        num_done_card_values = None
                    done_card_values_by_label[label.id].append(num_done_cards_with_this_label)

        date_i += timedelta(days=day_step)

    # Setting up chart values
    cumulative_chart.x_labels = x_labels
    cumulative_chart.add("Created cards", num_created_card_values)
    cumulative_chart.add("Done cards", num_done_card_values)
    if board:
        for label in labels:
            if sum(filter(None, created_card_values_by_label[label.id])) > 0:
                cumulative_chart.add("Created {0} cards in {1}".format(label.name, label.board.name), created_card_values_by_label[label.id])
            if sum(filter(None, done_card_values_by_label[label.id])) > 0:
                cumulative_chart.add("Done {0} cards in {1}".format(label.name, label.board.name), done_card_values_by_label[label.id])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=cumulative_chart.render(is_unicode=True))
    return chart.render_django_response()


# Cumulative developed card value throug time
def cumulative_value_evolution(current_user, board=None, day_step=1):
    return _value_evolution(current_user=current_user, board=board, cumulative=True, day_step=day_step)


# Evolution of developed card value through time
def value_evolution(current_user, board=None, day_step=1):
    return _value_evolution(current_user=current_user, board=board, cumulative=False, day_step=day_step)


# Evolution of developed card value by member
def value_evolution_by_member(current_user, board=None, day_step=1):
    return _value_evolution(current_user=current_user, board=board, cumulative=False, day_step=day_step, by_member=True)


# Evolution of developed card value through time
def _value_evolution(current_user, board=None, cumulative=False, day_step=1, by_member=False):
    # Caching
    chart_uuid = "cards.value_evolution-{0}-{1}-{2}-{3}".format(
        board.id if board else "all",
        "cumulative" if cumulative else "",
        day_step,
        "by_member" if by_member else ""
    )

    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    if cumulative:
        chart_title = u"Cumulative evolution of developed card value{0}as of {1}".format(" by member " if by_member else " ", timezone.now())
    else:
        chart_title = u"Evolution of developed card value{0}as of {1}".format(" by member " if by_member else " ", timezone.now())

    if board:
        chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    card_value_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, fill=False,
                                  x_labels_major_every=3, show_only_major_dots=True,
                                  show_minor_x_labels=False,
                                  human_readable=True, x_label_rotation=65)

    start_working_date = numpy.min(filter(None, [board_i.get_working_start_date() for board_i in boards]))
    end_working_date = numpy.max(filter(None, [board_i.get_working_end_date() for board_i in boards]))
    if start_working_date is None or end_working_date is None:
        return card_value_chart.render_django_response()

    local_timezone = pytz.timezone(settings.TIME_ZONE)

    if cumulative:
        def developed_value_sum(date_, member_=None):
            datetime_ = local_timezone.localize(datetime.combine(date_, time.min))
            card_movement_filter = {"board__in": boards, "destination_list__type": "done", "datetime__lte": datetime_}
            if member_:
                card_movement_filter["card__members"] = member_
            return CardMovement.objects.filter(**card_movement_filter).\
                aggregate(sum_of_developed_value=Sum("card__value"))["sum_of_developed_value"]
    else:
        def developed_value_sum(date_, member_=None):
            min_datetime_ = local_timezone.localize(datetime.combine(date_, time.min))
            max_datetime_ = local_timezone.localize(datetime.combine(date_, time.max))
            card_movement_filter = {
                "board__in": boards, "destination_list__type": "done",
                "datetime__gte": min_datetime_, "datetime__lte": max_datetime_
            }
            if member_:
                card_movement_filter["card__members"] = member_
            return CardMovement.objects.filter(**card_movement_filter).\
                aggregate(sum_of_developed_value=Sum("card__value"))["sum_of_developed_value"]

    date_i = copy.deepcopy(start_working_date)
    card_values = []
    x_labels = []

    members = Member.objects.filter(boards__in=boards, is_developer=True).distinct().order_by("id")
    card_values_by_member = {member_i.id: [] for member_i in members}

    while date_i <= end_working_date:
        sum_of_developed_value = developed_value_sum(date_i)
        if sum_of_developed_value is not None:
            x_labels.append(date_i)
            card_values.append(sum_of_developed_value)
            if by_member:
                for member in members:
                    member_developed_value = card_values.append(sum_of_developed_value, member)
                    if member_developed_value is not None:
                        card_values_by_member[member.id].append(member_developed_value)
        date_i += timedelta(days=day_step)

    card_value_chart.x_labels = x_labels
    card_value_chart.add("Team developed value", card_values)

    if by_member:
        for member in members:
            card_value_chart.add("{0}".format(member.external_username), card_values_by_member[member.id])

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=card_value_chart.render(is_unicode=True))
    return chart.render_django_response()


# Current age of each card per list in the board
def age(board):
    # Caching
    chart_uuid = "cards.age-{0}".format(board.id)
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Age box chart of tasks for {0} as of {1}".format(board.name, timezone.now())

    age_chart = pygal.Box(
        title=chart_title, legend_at_bottom=False, print_values=False, print_zeroes=False, fill=False,
        human_readable=True, x_label_rotation=65, stroke=False,
        x_title="List", y_title="Age (days)"
    )

    for list_ in board.lists.exclude(Q(type="done") | Q(type="closed")).order_by("position"):
        list_cards = list_.cards.exclude(is_closed=False).order_by("id")
        cards_age = [card.age.days for card in list_cards]
        age_chart.add(list_.name, cards_age)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=age_chart.render(is_unicode=True))
    return chart.render_django_response()


# Completion histogram for cards
def completion_histogram(current_user, board=None, time_metric="lead_time", units="days"):

    # Caching
    if board:
        chart_uuid = "cards.completion_histogram-{0}-{1}-{2}".format(board.id, time_metric, units)
    else:
        chart_uuid = "cards.completion_histogram-all-{0}-{1}".format(time_metric, units)

    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    time_metric_name = time_metric.replace("_", " ")
    if board:
        chart_title = u"{0} histogram for {1} as of {2}".format(time_metric_name, board.name, timezone.now())
    else:
        chart_title = u"{0} histogram for all boards as of {1}".format(time_metric_name, timezone.now())
    chart_title = chart_title.capitalize()

    completion_histogram_chart = pygal.Bar(
        title=chart_title, legend_at_bottom=False, print_values=False, print_zeroes=False, fill=False,
        human_readable=True, x_label_rotation=70, stroke=False,
        x_title=units.capitalize(), y_title="Number of cards completed")

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    cards = Card.objects.filter(board__in=boards, list__type="done")

    max_time = cards.exclude(is_closed=True).aggregate(max_time=Max(time_metric))["max_time"]

    if max_time is None:
        return completion_histogram_chart.render_django_response()

    # For each day we compute how many cards have been completed in that number of days
    x_labels = []
    num_card_values = []

    if units == "days":
        max_time_in_days = int(math.ceil(max_time / Decimal(24.0)))

        for days in range(1, max_time_in_days+1):
            hours_min = (days-1) * 24.0
            hours_max = days * 24.0
            card_filter = {"{0}__gt".format(time_metric): hours_min, "{0}__lte".format(time_metric): hours_max}
            num_cards = cards.filter(**card_filter).count()
            if num_cards > 0:
                x_labels.append(days)
                num_card_values.append(num_cards)

    elif units == "hours":
        for hours in range(1, max_time+1):
            hours_min = (hours - 1)
            card_filter = {"{0}__gt".format(time_metric): hours_min, "{0}__lte".format(time_metric): hours}
            num_cards = cards.filter(**card_filter).count()
            if num_cards > 0:
                x_labels.append(hours)
                num_card_values.append(num_cards)

    else:
        ValueError(u"Unknown units")

    completion_histogram_chart.x_labels = x_labels
    completion_histogram_chart.add(units.capitalize(), num_card_values)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=completion_histogram_chart.render(is_unicode=True))
    return chart.render_django_response()


# Scatterplot comparing the completion time vs. spent/lead/cycle time
def time_scatterplot(current_user, time_metric_name="Time", board=None,
                     y_function=lambda card: card.lead_time / Decimal(24) / Decimal(7),
                     year=None, month=None):

    # Caching
    chart_uuid = "cards.time_scatterplot-{0}-{1}-{2}-{3}-{4}".format(
        current_user.id, board.id if board else "None", inspect.getsource(y_function).strip(),
        year if year else "None", month if month else "None"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    if board:
        chart_title = u"{0} scatterplot of tasks for {1} as of {2}".format(time_metric_name, board.name, timezone.now())
    else:
        chart_title = u"{0} scatterplot of tasks for all boards as of {1}".format(time_metric_name, timezone.now())

    scatterplot = pygal.DateLine(
        title=chart_title, legend_at_bottom=False, print_values=False, print_zeroes=False, fill=False,
        human_readable=True, x_label_rotation=65, stroke=False,
        x_title="Completion date", y_title=time_metric_name
    )

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]

    start_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(start_working_date=Min("date"))[
        "start_working_date"]
    end_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(end_working_date=Max("date"))[
        "end_working_date"]

    if start_working_date is None or end_working_date is None:
        return scatterplot.render_django_response()

    month_i = 1
    end_month = end_working_date.month
    end_year = end_working_date.year

    if year is not None or month is not None:
        if year:
            year_i = int(year)
            end_year = int(year)
            if month:
                month_i = int(month)
                end_month = int(month)
    else:
        month_i = start_working_date.month
        year_i = start_working_date.year

        end_month = end_working_date.month
        end_year = end_working_date.year

    # Completed cards
    cards = Card.objects.filter(board__in=boards, is_closed=False, list__type="done").order_by("id")

    i = 0
    while (year_i == end_year and month_i <= end_month) or year_i < end_year:

        card_values = []
        cards_by_month = cards.filter(
            creation_datetime__month=month_i, creation_datetime__year=year_i,
            last_activity_datetime__month=month_i, last_activity_datetime__year=year_i
        )

        if cards_by_month.exists():
            for card in cards_by_month:
                try:
                    card_values.append((card.completion_datetime.date(), y_function(card)))
                # A TypeError is thrown when the y_function can't be computed because some of its parameters
                # are None. For example if a card is not done, spent_time will be None.
                except TypeError as e:
                    pass

            scatterplot.add("{0}-{1}".format(year_i, month_i), card_values)

        month_i += 1
        i += 1
        if month_i > 12:
            month_i = 1
            year_i += 1

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=scatterplot.render(is_unicode=True))
    return chart.render_django_response()


# Time vs. Spent Time
def time_vs_spent_time(current_user, time_metric_name="Time", board=None,
                       y_function=lambda card: card.lead_time,
                       year=None, month=None):

    # Caching
    chart_uuid = "cards.time_vs_spent_time-{0}-{1}-{2}-{3}-{4}".format(
        current_user.id, board.id if board else "None", inspect.getsource(y_function).strip(),
        year if year else "None", month if month else "None"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    now = timezone.now()
    if board:
        chart_title = u"{0} vs spent time of tasks for {1} as of {2}".format(time_metric_name, board.name, now)
    else:
        chart_title = u"{0} vs spent time of tasks for all boards as of {1}".format(time_metric_name, now)

    time_vs_spent_time_chart = pygal.XY(
        title=chart_title, legend_at_bottom=False, print_values=False, print_zeroes=False, fill=False,
        human_readable=True, x_label_rotation=65, stroke=False,
        x_title="Spent time (hours)", y_title=time_metric_name
    )

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]

    start_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(start_working_date=Min("date"))[
        "start_working_date"]
    end_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(end_working_date=Max("date"))[
        "end_working_date"]

    if start_working_date is None or end_working_date is None:
        return time_vs_spent_time_chart.render_django_response()

    month_i = 1
    end_month = end_working_date.month
    end_year = end_working_date.year

    if year is not None or month is not None:
        if year:
            year_i = int(year)
            end_year = int(year)
            if month:
                month_i = int(month)
                end_month = int(month)
    else:
        month_i = start_working_date.month
        year_i = start_working_date.year

        end_month = end_working_date.month
        end_year = end_working_date.year

    # Completed cards
    cards = Card.objects.filter(board__in=boards, is_closed=False, list__type="done").order_by("id")

    i = 0
    while (year_i == end_year and month_i <= end_month) or year_i < end_year:

        card_values = []
        cards_by_month = cards.filter(
            creation_datetime__month=month_i, creation_datetime__year=year_i,
            last_activity_datetime__month=month_i, last_activity_datetime__year=year_i
        )

        if cards_by_month.exists():
            for card in cards_by_month:
                try:
                    card_values.append((card.spent_time, y_function(card)))
                # A TypeError is thrown when the y_function can't be computed because some of its parameters
                # are None. For example if a card is not done, spent_time will be None.
                except TypeError:
                    pass

            time_vs_spent_time_chart.add("{0}-{1}".format(year_i, month_i), card_values)

        month_i += 1
        i += 1
        if month_i > 12:
            month_i = 1
            year_i += 1

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=time_vs_spent_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Box chart comparing the homogeneity of a time metric
def time_box(current_user, time_metric_name="Time", board=None,
             y_function=lambda card: card.lead_time / Decimal(24) / Decimal(7),
             year=None, month=None):

    # Caching
    chart_uuid = "cards.time_box-{0}-{1}-{2}-{3}-{4}".format(
        current_user.id, board.id if board else "None", inspect.getsource(y_function).strip(),
        year if year else "None", month if month else "None"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    if board:
        chart_title = u"{0} box chart of tasks for {1} as of {2}".format(time_metric_name, board.name, timezone.now())
    else:
        chart_title = u"{0} box chart of tasks for all boards as of {1}".format(time_metric_name, timezone.now())

    box_chart = pygal.Box(
        title=chart_title, legend_at_bottom=False, print_values=False, print_zeroes=False, fill=False,
        human_readable=True, x_label_rotation=65, stroke=False,
        x_title="Completion date", y_title=time_metric_name
    )

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]

    start_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(start_working_date=Min("date"))[
        "start_working_date"]
    end_working_date = DailySpentTime.objects.filter(board__in=boards).aggregate(end_working_date=Max("date"))[
        "end_working_date"]

    if start_working_date is None or end_working_date is None:
        return box_chart.render_django_response()

    month_i = 1
    end_month = end_working_date.month
    end_year = end_working_date.year

    if year is not None or month is not None:
        if year:
            year_i = int(year)
            end_year = int(year)
            if month:
                month_i = int(month)
                end_month = int(month)
    else:
        month_i = start_working_date.month
        year_i = start_working_date.year

        end_month = end_working_date.month
        end_year = end_working_date.year

    # Completed cards
    cards = Card.objects.filter(board__in=boards, is_closed=False, list__type="done").order_by("id")

    i = 0
    while (year_i == end_year and month_i <= end_month) or year_i < end_year:

        card_values = []
        cards_by_month = cards.filter(
            creation_datetime__month=month_i, creation_datetime__year=year_i,
            last_activity_datetime__month=month_i, last_activity_datetime__year=year_i
        )

        if cards_by_month.exists():
            for card in cards_by_month:
                try:
                    card_values.append(y_function(card))
                # A TypeError is thrown when the y_function can't be computed because some of its parameters
                # are None. For example if a card is not done, spent_time will be None.
                except TypeError:
                    pass

            box_chart.add("{0}-{1}".format(year_i, month_i), card_values)

        month_i += 1
        i += 1
        if month_i > 12:
            month_i = 1
            year_i += 1

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=box_chart.render(is_unicode=True))
    return chart.render_django_response()


# Number of comments chart
def number_of_comments(current_user, board=None, card=None):
    # Caching
    chart_uuid = "cards.number_of_comments-{0}-{1}-{2}".format(
        current_user.id, board.id if board else "None", card.id if card else "None"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Number of comments as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)
        if card:
            chart_title += u" for card '{0}'".format(card.name)
        chart_title += " (fetched on {0})".format(board.get_human_fetch_datetime())

    number_of_comments_chart = pygal.Line(
        title=chart_title, legend_at_bottom=True, print_values=False, print_zeroes=False, fill=False,
        margin=0, show_minor_x_labels=False, human_readable=True, x_label_rotation=65
    )

    card_comment_filter = {}
    if board:
        card_comment_filter["card__board"] = board
        if card:
            card_comment_filter["card"] = card
            number_of_comments_chart.show_minor_x_labels = True

    card_comments = CardComment.objects.filter(**card_comment_filter)

    # If there is no comments, render an empty chart
    if not card_comments.exists():
        return number_of_comments_chart.render_django_response()

    # Get datetime interval where all the comments were created
    start_datetime = card_comments.aggregate(min_creation_datetime=Min("creation_datetime"))["min_creation_datetime"]
    end_datetime = card_comments.aggregate(max_creation_datetime=Max("creation_datetime"))["max_creation_datetime"]

    start_date = start_datetime.date()
    end_date = end_datetime.date()

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    members = Member.objects.filter(boards__in=boards).distinct().order_by("id")

    number_of_comments_by_member = {member.id: [] for member in members}
    number_of_comments_list = []

    x_labels = []
    x_labels_major = []

    i = 1
    date_i = copy.deepcopy(start_date)
    while date_i <= end_date:
        # Number of comments
        comments = card_comments.filter(creation_datetime__date=date_i)
        # If there is at least a comment, is a day with comments
        if comments.exists():
            number_of_comments_list.append(comments.count())
            x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))
            if i == 1 or i % 5 == 0:
                x_labels_major.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))
            # Comments for each member
            for member in members:
                member_comments = comments.filter(author=member)
                number_of_comments_by_member[member.id].append(member_comments.count())
            i += 1

        date_i += timedelta(days=1)

    # Setting up chart values
    number_of_comments_chart.x_labels = x_labels
    number_of_comments_chart.x_labels_major = x_labels_major

    for member in members:
        if sum(number_of_comments_by_member[member.id]) > 0:
            number_of_comments_chart.add("{0}".format(member.external_username), number_of_comments_by_member[member.id])

    number_of_comments_chart.add("All members", number_of_comments_list)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=number_of_comments_chart.render(is_unicode=True))
    return chart.render_django_response()
