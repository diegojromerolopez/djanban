# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
from datetime import datetime, time, timedelta
import pygal
import calendar
from datetime import date

import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Min, Q, Count, Max
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board, Card, CardComment
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
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
def avg_time_by_list(board, workflow=None):
    chart_title = u"Average time of all tasks living in each list for board {0} ".format(board.name)
    if workflow:
        chart_title += "for workflow {0} ".format(workflow.name)

    chart_title += "as of {0}".format(board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    list_reports = ListReport.objects.filter(list__board=board)
    if workflow:
        list_reports = list_reports.filter(Q(list__in=workflow.lists.all()))
    for list_report in list_reports:
        avg_time_by_list_chart.add(u"{0}".format(list_report.list.name), list_report.avg_card_time)

    return avg_time_by_list_chart.render_django_response()


# Average card estimated time in each list
def avg_estimated_time_by_list(board, workflow=None):
    chart_title = u"Average estimated time of all tasks living in each list for board {0} ".format(board.name)
    if workflow:
        chart_title += "for workflow {0} ".format(workflow.name)

    chart_title += "as of {0}".format(board.get_human_fetch_datetime())

    avg_time_by_list_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                 print_zeroes=False,
                                                 human_readable=True)

    list_reports = ListReport.objects.filter(list__board=board)
    if workflow:
        list_reports = list_reports.filter(Q(list__in=workflow.lists.all()))
    for list_report in list_reports:
        avg_time_by_list_chart.add(u"{0}".format(list_report.list.name), list_report.std_dev_card_time)

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


# Cards-in cards-out
# Number of cards that are created vs number of cards that are completed along the live of the project
def cumulative_card_evolution(board, day_step=5):
    chart_title = u"Number of created cards vs completed cards as of {0}".format(timezone.now())
    chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    cumulative_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                  print_zeroes=False, fill=False,
                                  human_readable=True, x_label_rotation=45)

    start_working_date = board.get_working_start_date()
    if start_working_date is None:
        return cumulative_chart.render_django_response()

    end_working_date = board.get_working_end_date()
    if end_working_date is None:
        return cumulative_chart.render_django_response()

    # Labels of the board
    labels = board.labels.exclude(name="").order_by("name")

    # Number of created cards by label
    created_card_values_by_label = {label.id: [] for label in labels}

    # Number of done cards by label
    done_card_values_by_label = {label.id: [] for label in labels}

    # Done list
    done_list = board.lists.get(type="done")

    num_created_card_values = []
    num_done_card_values = []

    x_labels = []

    date_i = copy.deepcopy(start_working_date)
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    while date_i <= end_working_date:
        datetime_i = local_timezone.localize(datetime.combine(date_i, time.min))

        # Created cards that were created in this list before the date
        created_cards = board.cards.filter(creation_datetime__lte=datetime_i)

        # Number of created cards that were created in this list before the date
        num_created_cards = created_cards.count()

        # Cards that were moved to this list before the date
        done_cards = board.card_movements.filter(destination_list=done_list,
                                                 datetime__lte=datetime_i)

        # Number of cards that were moved to this list before the date
        num_done_cards = done_cards.count()

        # When there has been created or terminated any card
        if num_created_cards > 0 or num_done_cards > 0:
            num_created_card_values.append(num_created_cards)
            num_done_card_values.append(num_done_cards)
            x_labels.append(u"{0}-{1}-{2}".format(date_i.year, date_i.month, date_i.day))

            # Each category filtered by label
            for label in labels:
                created_card_values_by_label[label.id].append(
                    label.cards.filter(id__in=created_cards).count()
                )
                done_card_values_by_label[label.id].append(
                    label.cards.filter(id__in=done_cards).count()
                )

        date_i += timedelta(days=day_step)

    # Setting up chart values
    cumulative_chart.x_labels = x_labels
    cumulative_chart.add("Created cards", num_created_card_values)
    cumulative_chart.add("Done", num_done_card_values)
    for label in labels:
        cumulative_chart.add("Created {0} cards".format(label.name), created_card_values_by_label[label.id])
        cumulative_chart.add("Done {0} cards".format(label.name), done_card_values_by_label[label.id])

    return cumulative_chart.render_django_response()


# Number of comments chart
def number_of_comments(current_user, board=None, card=None):
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

    members = Member.objects.filter(boards__in=boards).distinct().order_by("initials")

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
    number_of_comments_chart.add("Total number of comments", number_of_comments_list)

    for member in members:
        if sum(number_of_comments_by_member[member.id]) > 0:
            number_of_comments_chart.add("{0}".format(member.trello_username), number_of_comments_by_member[member.id])

    return number_of_comments_chart.render_django_response()
