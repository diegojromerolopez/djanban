# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import pygal
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.charts import boards, cards, labels, members, interruptions, noise_measurements,\
    repositories, requirements
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.utils.week import get_iso_week_of_year


# Requirement burndown chart
@login_required
def requirement_burndown(request, board_id, requirement_code=None):
    requirement = None
    board = get_user_boards(request.user).get(id=board_id)
    if requirement_code is not None:
        requirement = board.requirements.get(code=requirement_code)
    return requirements.burndown(board, requirement)


# Burndown according to estimates and spent times (not requirements)
@login_required
def burndown(request, board_id):
    board = get_user_boards(request.user).get(id=board_id)
    return boards.burndown(board)


# Average card lead time
@login_required
def avg_lead_time(request, board_id=None):
    board = None
    if board_id is not None:
        board = get_user_boards(request.user).get(id=board_id)
    return cards.avg_lead_time(request, board)


# Average card cycle time
@login_required
def avg_cycle_time(request, board_id=None):
    board = None
    if board_id is not None:
        board = get_user_boards(request.user).get(id=board_id)
    return cards.avg_cycle_time(request, board)


# Average time by board list
@login_required
def avg_time_by_list(request, board_id, workflow_id=None):
    board = get_user_boards(request.user).get(id=board_id)
    workflow = None
    if board.workflows.filter(id=workflow_id).exists():
        workflow = board.workflows.get(id=workflow_id)
    return cards.avg_time_by_list(board, workflow)


# Average estimated time by list
@login_required
def avg_estimated_time_by_list(request, board_id, workflow_id=None):
    board = get_user_boards(request.user).get(id=board_id)
    workflow = None
    if board.workflows.filter(id=workflow_id).exists():
        workflow = board.workflows.get(id=workflow_id)
    return cards.avg_estimated_time_by_list(board, workflow)


# Average spent time by label
@login_required
def avg_spent_times(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.avg_spent_times(request, board)


# Average spent time by month
@login_required
def avg_spent_time_by_month(request, board_id):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.avg_spent_time_by_month(board)


# Average estimated times
@login_required
def avg_estimated_times(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.avg_estimated_times(request, board)


# Average estimated time by month
@login_required
def avg_estimated_time_by_month(request, board_id):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.avg_estimated_time_by_month(board)


# Number of tasks by month
@login_required
def number_of_cards_worked_on_by_month(request, board_id):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.number_of_cards_worked_on_by_month(board)


# Number of tasks by week
@login_required
def number_of_cards_worked_on_by_week(request, board_id):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return labels.number_of_cards_worked_on_by_week(board)


# Show a chart with the task forward movements by member
@login_required
def task_forward_movements_by_member(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return members.task_movements_by_member("forward", board)


# Show a chart with the task backward movements by member
@login_required
def task_backward_movements_by_member(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return members.task_movements_by_member("backward", board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_week(request, week_of_year=None, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return members.spent_time_by_week(request.user, week_of_year=week_of_year, board=board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_day_of_the_week(request, member_id=None, week_of_year=None, board_id=None):
    if member_id is None:
        if hasattr(request.user, "member") and request.user.member:
            member = request.user.member
        else:
            boards = get_user_boards(request.user)
            member = Member.objects.filter(boards__in=boards)[0]
    else:
        member = Member.objects.get(id=member_id)

    if week_of_year is None:
        now = timezone.now()
        today = now.date()
        week_of_year_ = get_iso_week_of_year(today)
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


@login_required
def spent_time_by_week_evolution(request, board_id):
    board = get_user_boards(request.user).get(id=board_id)
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return members.spent_time_by_week_evolution(board=board)


@login_required
def cumulative_list_evolution(request, board_id, day_step=5):
    board = get_user_boards(request.user).get(id=board_id)
    if day_step is None:
        day_step = 5
    day_step = min(int(day_step), 30)
    return cards.cumulative_list_evolution(board, day_step)


@login_required
def cumulative_card_evolution(request, board_id, day_step=5):
    board = get_user_boards(request.user).get(id=board_id)
    if day_step is None:
        day_step = 5
    day_step = min(int(day_step), 30)
    return cards.cumulative_card_evolution(board, day_step)


# Interruptions
@login_required
def number_of_interruptions(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return interruptions.number_of_interruptions(board)


# Interruptions
@login_required
def number_of_interruptions_by_month(request, board_id=None):
    board = None
    if board_id:
        board = get_user_boards(request.user).get(id=board_id)
    return interruptions.number_of_interruptions_by_month(request.user, board)


# Noise measurements
@login_required
def noise_level(request):
    return noise_measurements.noise_level()


@login_required
def subjective_noise_level(request):
    return noise_measurements.subjective_noise_level()


# Code quality
@login_required
def number_of_code_errors_by_month(request, board_id, repository_id=None, language="python"):
    board = get_user_boards(request.user).get(id=board_id)
    repository = None
    if repository_id:
        repository = board.repositories.get(id=repository_id)
    if language is None:
        language = "python"
    return repositories.number_of_code_errors_by_month(board, repository, language)


@login_required
def number_of_code_errors_per_loc_by_month(request, board_id, repository_id=None, language="python"):
    board = get_user_boards(request.user).get(id=board_id)
    repository = None
    if repository_id:
        repository = board.repositories.get(id=repository_id)
    if language is None:
        language = "python"
    return repositories.number_of_code_errors_per_loc_by_month(board, repository, language)


