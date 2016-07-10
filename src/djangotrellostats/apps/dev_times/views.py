# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http.response import Http404
from django.shortcuts import render

from djangotrellostats.apps.boards.models import Fetch, DailySpentTime, Board
from djangotrellostats.apps.members.models import Member


# View spent time report
@login_required
def view_daily_spent_times(request):
    member = request.user.member

    try:
        last_fetch = Fetch.last()
    except Fetch.DoesNotExist:
        raise Http404

    daily_spent_time_filter = {"fetch": last_fetch}
    replacements = {"fetch": last_fetch, "boards": Board.objects.all(), "members": Member.objects.all()}

    # Start date
    start_date_str = request.GET.get("start_date")
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            replacements["start_date"] = start_date
            daily_spent_time_filter["date__gte"] = start_date
        except ValueError:
            start_date = None

    # Start date
    end_date_str = request.GET.get("end_date")
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            replacements["end_date"] = end_date
            daily_spent_time_filter["date__lte"] = end_date
        except ValueError:
            end_date = None

    # Member whose time report we want to see
    member_id = request.GET.get("member_id")
    if member_id:
        selected_member = Member.objects.get(id=member_id)
        replacements["selected_member"] = selected_member
        daily_spent_time_filter["member"] = selected_member

    # If we are filtering by board, filter by board_id
    board_id = request.GET.get("board_id")
    if board_id:
        board = member.boards.get(id=board_id)
        replacements["selected_board"] = board
        daily_spent_time_filter["board"] = board

    daily_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).order_by("-date")
    replacements["daily_spent_times"] = daily_spent_times
    replacements["spent_time_sum"] = daily_spent_times.aggregate(Sum("spent_time"))["spent_time__sum"]
    replacements["estimated_time_sum"] = daily_spent_times.aggregate(Sum("estimated_time"))["estimated_time__sum"]
    replacements["diff_time_sum"] = daily_spent_times.aggregate(Sum("diff_time"))["diff_time__sum"]

    return render(request, "daily_spent_times/list.html", replacements)
