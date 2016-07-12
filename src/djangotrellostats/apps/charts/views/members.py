# -*- coding: utf-8 -*-
import copy

import pygal
from django.db.models import Sum
from django.utils import timezone

from djangotrellostats.apps.boards.models import MemberReport, Board
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member


# Show a chart with the task forward movements by member
def task_forward_movements_by_member(request, board_id=None):
    return _task_movements_by_member(request, "forward", board_id)


# Show a chart with the task backward movements by member
def task_backward_movements_by_member(request, board_id=None):
    return _task_movements_by_member(request, "backward", board_id)


# Show a chart with the task movements (backward or forward) by member
def _task_movements_by_member(request, movement_type="forward", board_id=None):

    if movement_type != "forward" and movement_type != "backward":
        raise ValueError("{0} is not recognized as a valid movement type".format(movement_type))

    chart_title = u"Task {0} movements as of {1}".format(movement_type, timezone.now())
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    member_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    report_filter = {}
    if board_id:
        report_filter["board_id"] = board_id

    members = Member.objects.all()

    for member in members:
        member_name = member.trello_username

        member_report_filter = copy.deepcopy(report_filter)
        member_report_filter["member"] = member

        try:
            member_report = MemberReport.objects.get(**member_report_filter )

            if movement_type == "forward":
                member_chart.add(u"{0}'s tasks forward movements".format(member_name), member_report.forward_movements)
            elif movement_type == "backward":
                member_chart.add(u"{0}'s tasks backward movements".format(member_name), member_report.backward_movements)

        except MemberReport.DoesNotExist:
            pass

    return member_chart.render_django_response()


# Show a chart with the
def spent_time_by_week(request, week_of_year=None, board_id=None):

    if week_of_year is None:
        now = timezone.now()
        today = now.date()
        week_of_year = DailySpentTime.get_iso_week_of_year(today)

    chart_title = u"Spent time in week {0}".format(week_of_year)
    if board_id:
        board = Board.objects.get(id=board_id)
        chart_title += u" for board {0}".format(board.name)

    spent_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True)

    report_filter = {"week_of_year": week_of_year}
    if board_id:
        report_filter["board_id"] = board_id

    members = Member.objects.all()

    for member in members:
        member_name = member.trello_username

        daily_spent_times = member.daily_spent_times.filter(**report_filter)
        spent_time = daily_spent_times.aggregate(Sum("spent_time"))["spent_time__sum"]
        if spent_time is None:
            spent_time = 0

        if spent_time > 0:
            spent_time_chart.add(u"{0}'s spent time".format(member_name), spent_time)

    return spent_time_chart.render_django_response()