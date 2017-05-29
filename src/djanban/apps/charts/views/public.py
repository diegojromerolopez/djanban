# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djanban.apps.base.auth import user_is_administrator
from djanban.apps.boards.models import Board
from djanban.apps.charts import cards, labels, members, boards, requirements


# General burndown chart
def burndown(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return boards.burndown(board=board)


# Requirement burndown chart
def requirement_burndown(request, board_public_access_code, requirement_code=None):
    requirement = None
    board = _get_user_board(request, board_public_access_code)
    if requirement_code is not None:
        requirement = board.requirements.get(code=requirement_code)
    return requirements.burndown(board, requirement)


# Show the spent time by week by members
def spent_time_by_week(request, week_of_year, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return members.spent_time_by_week(request.user, week_of_year=week_of_year, board=board)


# Show a chart with the task forward movements by member
def task_forward_movements_by_member(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return members.task_movements_by_member(request, "forward", board)


# Show a chart with the task backward movements by member
def task_backward_movements_by_member(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return members.task_movements_by_member(request, "backward", board)


# Show average time each card lives in each list
def avg_time_by_list(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return cards.avg_time_by_list(board)


# Average card lead time
def avg_lead_time(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return cards.avg_lead_time(request, board)


# Average card cycle time
def avg_cycle_time(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return cards.avg_cycle_time(request, board)


# Average spent times
def avg_spent_times(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return labels.avg_spent_times(request, board)


# Average estimated times
def avg_estimated_times(request, board_public_access_code):
    board = _get_user_board(request, board_public_access_code)
    return labels.avg_estimated_times(request, board)


# Get user boards depending on if the user is a superuser
# or a visitor
def _get_user_board(request, board_public_access_code):
    if user_is_administrator(request.user):
        return Board.objects.get(public_access_code=board_public_access_code)
    return Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
