# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import pygal
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.base.auth import get_user_boards, user_is_member
from djangotrellostats.apps.charts import boards, cards, labels, members, interruptions, noise_measurements,\
    repositories, requirements, agility_rating
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
    return boards.burndown(board, show_interruptions=request.GET.get("show_interruptions"))


# Average card lead time
@login_required
def avg_lead_time(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return cards.avg_lead_time(request, board)


# Average card lead time by month
@login_required
def avg_lead_time_by_month(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return cards.avg_lead_time_by_month(request, board)


# Average card cycle time
@login_required
def avg_cycle_time(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return cards.avg_cycle_time(request, board)


# Average card cycle time by month
@login_required
def avg_cycle_time_by_month(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return cards.avg_cycle_time_by_month(request, board)


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
def avg_std_dev_time_by_list(request, board_id, workflow_id=None):
    board = get_user_boards(request.user).get(id=board_id)
    workflow = None
    if board.workflows.filter(id=workflow_id).exists():
        workflow = board.workflows.get(id=workflow_id)
    return cards.avg_std_dev_time_by_list(board, workflow)


# Average spent time by label
@login_required
def avg_spent_times(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return labels.avg_spent_times(request, board)


# Average spent time by month
@login_required
def avg_spent_time_by_month(request, board_id):
    board = _get_user_board_or_none(request, board_id)
    return labels.avg_spent_time_by_month(board)


# Average estimated times
@login_required
def avg_estimated_times(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return labels.avg_estimated_times(request, board)


# Average estimated time by month
@login_required
def avg_estimated_time_by_month(request, board_id):
    board = _get_user_board_or_none(request, board_id)
    return labels.avg_estimated_time_by_month(board)


# Number of tasks by month
@login_required
def number_of_cards_worked_on_by_month(request, board_id):
    board = _get_user_board_or_none(request, board_id)
    return labels.number_of_cards_worked_on_by_month(board)


# Number of tasks by week
@login_required
def number_of_cards_worked_on_by_week(request, board_id):
    board = _get_user_board_or_none(request, board_id)
    return labels.number_of_cards_worked_on_by_week(board)


# Show a chart with the task forward movements by member
@login_required
def task_forward_movements_by_member(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return members.task_movements_by_member("forward", board)


# Show a chart with the task backward movements by member
@login_required
def task_backward_movements_by_member(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return members.task_movements_by_member("backward", board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_week(request, week_of_year=None, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return members.spent_time_by_week(request.user, week_of_year=week_of_year, board=board)


# Show a chart with the spent time by week by member and by board
@login_required
def spent_time_by_day_of_the_week(request, member_id=None, week_of_year=None, board_id=None):
    user_boards = get_user_boards(request.user)
    if member_id is None:
        if user_is_member(request.user):
            member = request.user.member
        else:
            member = Member.objects.filter(boards__in=user_boards)[0]
    else:
        member = Member.objects.filter(boards__in=user_boards).distinct().get(id=member_id)

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
        board = user_boards.get(id=board_id)
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
    board = _get_user_board_or_none(request, board_id)
    return members.spent_time_by_week_evolution(board=board, show_interruptions=request.GET.get("show_interruptions"))


@login_required
def avg_spent_time_by_weekday(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return members.avg_spent_time_by_weekday(request.user, board)


@login_required
def absolute_flow_diagram(request, board_id, day_step=1):
    board = get_user_boards(request.user).get(id=board_id)

    if day_step is None:
        day_step = 1

    day_step = min(int(day_step), 30)
    return cards.absolute_flow_diagram(board, day_step)


@login_required
def cumulative_flow_diagram(request, board_id, day_step=1):
    board = get_user_boards(request.user).get(id=board_id)

    if day_step is None:
        day_step = 1

    day_step = min(int(day_step), 30)
    return cards.cumulative_flow_diagram(board, day_step)


@login_required
def cumulative_list_type_evolution(request, board_id, day_step=1):
    if board_id != "all":
        board = get_user_boards(request.user).get(id=board_id)
    else:
        board = None

    if day_step is None:
        day_step = 1

    day_step = min(int(day_step), 30)
    return cards.cumulative_list_type_evolution(request.user, board, day_step)


@login_required
def cumulative_card_evolution(request, board_id="all", day_step=1):
    if board_id != "all":
        board = get_user_boards(request.user).get(id=board_id)
    else:
        board = None

    if day_step is None:
        day_step = 1

    day_step = min(int(day_step), 30)
    return cards.cumulative_card_evolution(request.user, board, day_step)


@login_required
def number_of_comments(request, board_id=None, card_id=None):
    board = None
    card = None
    if board_id is not None:
        board = get_user_boards(request.user).get(id=board_id)
        if card_id is not None:
            card = board.cards.get(id=card_id)
    return cards.number_of_comments(request.user, board, card)


@login_required
def number_of_comments_by_member(request, board_id=None, card_id=None):
    board = None
    card = None
    if board_id is not None:
        board = get_user_boards(request.user).get(id=board_id)
        if card_id is not None:
            card = board.cards.get(id=card_id)
    return members.number_of_comments(request.user, board, card)


@login_required
def number_of_cards_by_member(request, board_id=None):
    board = None
    if board_id is not None:
        board = get_user_boards(request.user).get(id=board_id)
    return members.number_of_cards(request.user, board)


@login_required
def spent_time_by_member(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return members.spent_time(request.user, board)


# Interruptions
@login_required
def number_of_interruptions(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.number_of_interruptions(request.user, board)


# Evolution of the number of interruptions
@login_required
def evolution_of_number_of_interruptions(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.evolution_of_interruptions(request.user, board)


# Interruption spent time
@login_required
def interruption_spent_time(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.interruption_spent_time(request.user, board)


# Scatterplot comparing the completion date vs. some time metric
@login_required
def time_scatterplot(request, time_metric, board_id=None, year=None, month=None):
    board = _get_user_board_or_none(request, board_id)
    if time_metric == "lead_time":
        y_function = lambda card: card.lead_time/Decimal(24)/Decimal(7)
        time_metric_name = "Lead time (in weeks)"
    elif time_metric == "cycle_time":
        y_function = lambda card: card.cycle_time / Decimal(24) / Decimal(7)
        time_metric_name = "Cycle time (in weeks)"
    elif time_metric == "spent_time":
        y_function = lambda card: card.spent_time
        time_metric_name = "Spent time (in days)"
    else:
        raise ValueError(u"Time metric {0} not recognized".format(time_metric))
    return cards.time_scatterplot(request.user, time_metric_name, board, y_function=y_function, year=year, month=month)


# Scatterplot comparing the completion date vs. some time metric
@login_required
def time_box(request, time_metric, board_id=None, year=None, month=None):
    board = _get_user_board_or_none(request, board_id)
    if time_metric == "lead_time":
        y_function = lambda card: card.lead_time/Decimal(24)/Decimal(7)
        time_metric_name = "Lead time (in weeks)"
    elif time_metric == "cycle_time":
        y_function = lambda card: card.cycle_time/Decimal(24)/Decimal(7)
        time_metric_name = "Cycle time (in weeks)"
    elif time_metric == "spent_time":
        y_function = lambda card: card.spent_time
        time_metric_name = "Spent time (days)"
    else:
        raise ValueError(u"Time metric {0} not recognized".format(time_metric))
    return cards.time_box(request.user, time_metric_name, board, y_function=y_function, year=year, month=month)


# Completion histogram
@login_required
def completion_histogram(request, board_id="all", time_metric="lead_time", units="days"):
    if board_id != "all":
        board = _get_user_board_or_none(request, board_id)
    else:
        board = None

    if time_metric is None:
        time_metric = "lead_time"
    elif time_metric != "lead_time" and time_metric != "cycle_time" and time_metric != "spent_time":
        raise ValueError(u"Time metric {0} not recognized".format(time_metric))

    if units is None:
        units = "days"
    elif units != "days" and units != "hours":
        raise ValueError(u"Units value {0} not recognized".format(units))

    return cards.completion_histogram(request.user, board, time_metric, units)


# Lead/Cycle Time vs Spent time
@login_required
def time_vs_spent_time(request, time_metric, board_id=None, year=None, month=None):
    board = _get_user_board_or_none(request, board_id)
    if time_metric == "lead_time":
        y_function = lambda card: card.lead_time/Decimal(24)
        time_metric_name = "Lead time (days)"
    elif time_metric == "cycle_time":
        y_function = lambda card: card.cycle_time/Decimal(24)
        time_metric_name = "Cycle time (days)"
    else:
        raise ValueError(u"Time metric {0} not recognized".format(time_metric))
    return cards.time_vs_spent_time(request.user, time_metric_name, board,
                                    y_function=y_function, year=year, month=month)


# Card age per list box chart
@login_required
def card_age(request, board_id):
    board = _get_user_board_or_none(request, board_id)
    return cards.age(board)


# Evolution of the interruption spent time
@login_required
def evolution_of_interruption_spent_time(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.evolution_of_interruption_spent_time(request.user, board)


# Number of interruptions by member
@login_required
def number_of_interruptions_by_member(request):
    return interruptions.number_of_interruptions_by_member(request.user)


@login_required
def interruption_spent_time_by_member(request):
    return interruptions.interruption_spent_time_by_member(request.user)


# Interruptions
@login_required
def number_of_interruptions_by_month(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.number_of_interruptions_by_month(request.user, board)


@login_required
def interruption_spent_time_by_month(request, board_id=None):
    board = _get_user_board_or_none(request, board_id)
    return interruptions.interruption_spent_time_by_month(request.user, board)


# Noise level measurements
@login_required
def noise_level(request):
    return noise_measurements.noise_level(request.user)


# Average noise level per hour
@login_required
def noise_level_per_hour(request):
    return noise_measurements.noise_level_per_hour(request.user)


# Average noise level per hour
@login_required
def noise_level_per_weekday(request):
    return noise_measurements.noise_level_per_weekday(request.user)


@login_required
def subjective_noise_level(request):
    return noise_measurements.subjective_noise_level(request.user)


# Code quality
@login_required
def number_of_code_errors(request, grouped_by, board_id, repository_id=None, language="python"):
    board = get_user_boards(request.user).get(id=board_id)
    repository = None
    if repository_id:
        repository = board.repositories.get(id=repository_id)
    if language is None:
        language = "python"
    return repositories.number_of_code_errors(grouped_by, board, repository, language)


@login_required
def number_of_code_errors_per_loc(request, grouped_by, board_id, repository_id=None, language="python"):
    board = get_user_boards(request.user).get(id=board_id)
    repository = None
    if repository_id:
        repository = board.repositories.get(id=repository_id)
    if language is None:
        language = "python"
    return repositories.number_of_code_errors_per_loc(grouped_by, board, repository, language)


# Agility rating
@login_required
def view_agility_rating(request, board_id):
    board = get_user_boards(request.user).get(id=board_id)
    return agility_rating.view(board)


# Get user board or None according to the board_id parameter
def _get_user_board_or_none(request, board_id=None):
    if board_id is None:
        return None
    board = get_user_boards(request.user).get(id=board_id)
    return board
