# -*- coding: utf-8 -*-

import datetime

import pygal
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.charts import cards, labels, members
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member


# Average card lead time
@login_required
def avg_lead_time(request, board_id=None):
    board = None
    if board_id is not None:
        board = request.user.member.boards.get(id=board_id)
    return cards.avg_lead_time(request, board)


# Average card cycle time
@login_required
def avg_cycle_time(request, board_id=None):
    board = None
    if board_id is not None:
        board = request.user.member.boards.get(id=board_id)
    return cards.avg_cycle_time(request, board)


# Average time by board list
@login_required
def avg_time_by_list(request, board_id):
    board = request.user.member.boards.get(id=board_id)
    return cards.avg_time_by_list(board)


# Average spent time by label
@login_required
def avg_spent_times(request, board_id=None):
    board = None
    if board_id:
        board = request.user.member.boards.get(id=board_id)
    return labels.avg_spent_times(request, board)


# Average estimated times
@login_required
def avg_estimated_times(request, board_id=None):
    board = None
    if board_id:
        board = request.user.member.boards.get(id=board_id)
    return labels.avg_estimated_times(request, board)


# Show a chart with the task forward movements by member
@login_required
def task_forward_movements_by_member(request, board_id=None):
    board = None
    if board_id:
        board = request.user.member.boards.get(id=board_id)
    return members.task_movements_by_member("forward", board)


# Show a chart with the task backward movements by member
@login_required
def task_backward_movements_by_member(request, board_id=None):
    board = None
    if board_id:
        board = request.user.member.boards.get(id=board_id)
    return members.task_movements_by_member("backward", board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_week(request, week_of_year=None, board_id=None):
    board = None
    if board_id:
        board = request.user.member.boards.get(id=board_id)
    return members.spent_time_by_week(week_of_year=week_of_year, board=board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_day_of_the_week(request, member_id=None, week_of_year=None, board_id=None):
    if member_id is None:
        member = request.user.member
    else:
        member = Member.objects.get(id=member_id)

    if week_of_year is None:
        now = timezone.now()
        today = now.date()
        week_of_year_ = DailySpentTime.get_iso_week_of_year(today)
        week_of_year = "{0}W{1}".format(today.year, week_of_year_)

    y, w = week_of_year.split("W")
    week = Week(int(y), int(w))
    start_of_week = week.monday()
    end_of_week = week.sunday()

    chart_title = u"{0}'s spent time in week {1} ({2} - {3})".format(member.trello_username, week_of_year,
                                                                     start_of_week.strftime("%Y-%m-%d"),
                                                                     end_of_week.strftime("%Y-%m-%d"))
    board = None
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    spent_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False,
                                           human_readable=True)

    day = start_of_week
    while day <= end_of_week:
        spent_time_chart.add(u"{0}".format(day.strftime("%A")), member.get_spent_time(day, board))
        day += datetime.timedelta(days=1)

    return spent_time_chart.render_django_response()