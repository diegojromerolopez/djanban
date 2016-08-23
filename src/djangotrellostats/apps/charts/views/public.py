

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.charts.views.cards import _avg_time_by_list, _avg_lead_time, _avg_cycle_time
from djangotrellostats.apps.charts.views.labels import _avg_spent_times, _avg_estimated_times
from djangotrellostats.apps.charts.views.members import _task_movements_by_member, _spent_time_by_week


def spent_time_by_week(request, week_of_year, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _spent_time_by_week(week_of_year=week_of_year, board=board)

# Show a chart with the task forward movements by member
def task_forward_movements_by_member(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _task_movements_by_member("forward", board)


# Show a chart with the task backward movements by member
def task_backward_movements_by_member(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _task_movements_by_member("backward", board)


# Show average time each card lives in each list
def avg_time_by_list(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _avg_time_by_list(board)


# Average card lead time
def avg_lead_time(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _avg_lead_time(request, board)


# Average card cycle time
def avg_cycle_time(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _avg_cycle_time(request, board)


# Average spent times
def avg_spent_times(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _avg_spent_times(request, board)


# Average estimated times
def avg_estimated_times(request, board_public_access_code):
    board = Board.objects.get(enable_public_access=True, public_access_code=board_public_access_code)
    return _avg_estimated_times(request, board)
