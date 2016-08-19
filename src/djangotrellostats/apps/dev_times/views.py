# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.http.response import Http404, HttpResponse
from django.shortcuts import render

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from django.template import loader, Context
import calendar


# View spent time report
@login_required
def view_daily_spent_times(request):
    parameters = _get_daily_spent_times_replacements(request)

    if "board" in parameters["replacements"] and parameters["replacements"]["board"]:
        return render(request, "daily_spent_times/list_by_board.html", parameters["replacements"])
    return render(request, "daily_spent_times/list.html", parameters["replacements"])


# Export daily spent report in CSV format
@login_required
def export_daily_spent_times(request):
    spent_times = _get_daily_spent_times_from_request(request)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export-daily-spent-times.csv"'

    csv_template = loader.get_template('daily_spent_times/csv.txt')
    replacements = Context({
        'spent_times': spent_times["all"],
    })
    response.write(csv_template.render(replacements))
    return response


# Return the filtered queryset and the replacements given the GET parameters
def _get_daily_spent_times_replacements(request):
    current_member = request.user.member

    selected_member_id = request.GET.get("member_id")
    selected_member = None
    if selected_member_id:
        selected_member = Member.objects.get(id=selected_member_id)

    spent_times = _get_daily_spent_times_from_request(request)

    replacements = {"boards": Board.objects.all(), "members": Member.objects.all()}

    # Start date
    start_date_str = request.GET.get("start_date")
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            replacements["start_date"] = start_date
        except ValueError:
            start_date = None

    # Start date
    end_date_str = request.GET.get("end_date")
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            replacements["end_date"] = end_date
        except ValueError:
            end_date = None

    replacements["selected_member"] = selected_member

    # If we are filtering by board, filter by board_id
    board_id = request.GET.get("board_id")
    board = None
    if board_id:
        board = current_member.boards.get(id=board_id)
        replacements["selected_board"] = board
        replacements["board"] = board

    daily_spent_times = spent_times["all"]
    replacements["week"] = request.GET.get('week') if request.GET.get('week') and request.GET.get('week') > 0 else None
    replacements["months"] = spent_times["per_month"]
    replacements["spent_time_sum"] = daily_spent_times.aggregate(Sum("spent_time"))["spent_time__sum"]
    replacements["spent_time_amount_sum"] = daily_spent_times.aggregate(Sum("rate_amount"))["rate_amount__sum"]
    replacements["estimated_time_sum"] = daily_spent_times.aggregate(Sum("estimated_time"))["estimated_time__sum"]
    replacements["diff_time_sum"] = daily_spent_times.aggregate(Sum("diff_time"))["diff_time__sum"]

    return {"queryset": daily_spent_times, "replacements": replacements}


# Return the daily spent times from a request
def _get_daily_spent_times_from_request(request):
    current_member = request.user.member
    selected_member = None
    if request.GET.get("member_id"):
        selected_member = Member.objects.get(id=request.GET.get("member_id"))

    spent_times = _get_daily_spent_times_queryset(current_member, selected_member,
                                                  request.GET.get("start_date"), request.GET.get("end_date"),
                                                  request.GET.get('week'),
                                                  request.GET.get("board_id"))

    return spent_times


# Return the filtered queryset and the replacements given the GET parameters
def _get_daily_spent_times_queryset(current_member, selected_member, start_date_, end_date_, week, board_id):
    daily_spent_time_filter = {}

    # Member filter
    if selected_member:
        daily_spent_time_filter["member_id"] = selected_member.id

    # Start date
    start_date = None
    if start_date_:
        try:
            start_date = datetime.datetime.strptime(start_date_, "%Y-%m-%d")
            daily_spent_time_filter["date__gte"] = start_date
        except ValueError:
            start_date = None

    # End date
    end_date = None
    if end_date_:
        try:
            end_date = datetime.datetime.strptime(end_date_, "%Y-%m-%d")
            daily_spent_time_filter["date__lte"] = end_date
        except ValueError:
            end_date = None

    # Week
    if week and week > 0:
        daily_spent_time_filter["week_of_year"] = week

    # Board
    if board_id and current_member.boards.filter(id=board_id).exists():
        daily_spent_time_filter["board_id"] = board_id

    # Daily Spent Times
    daily_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).order_by("-date")
    months = []

    # Grouped by months
    if daily_spent_times.exists():
        if start_date is None:
            start_date = daily_spent_times.order_by("date")[0].date

        if end_date is None:
            end_date = daily_spent_times[0].date

        num_months = absolute_difference_between_months(start_date, end_date) + 1
        months = []
        year = start_date.year
        for i in range(0, num_months):
            month_index = start_date.month + i

            # TODO: delete this condition if is not needed
            if month_index > 12:
                break

            month_name = calendar.month_name[month_index]
            daily_spent_times_in_month_i = daily_spent_times.filter(date__month=month_index).order_by("date")

            month = {
                "name": month_name,
                "number": month_index,
                "year": year,
                "i": month_index,
                "daily_spent_times": daily_spent_times_in_month_i,
                "rate_amount_sum": daily_spent_times_in_month_i.aggregate(sum=Sum("rate_amount"))["sum"],
                "spent_time_sum": daily_spent_times_in_month_i.aggregate(sum=Sum("spent_time"))["sum"],
                "estimated_time_sum": daily_spent_times_in_month_i.aggregate(sum=Sum("estimated_time"))["sum"],
                "diff_time_sum": daily_spent_times_in_month_i.aggregate(sum=Sum("diff_time"))["sum"]
            }
            months.append(month)
            if month == 12:
                year += 1

    return {"all": daily_spent_times, "per_month": months}


def absolute_difference_between_months(d1, d2):
    return abs((d1.year - d2.year) * 12 + d1.month - d2.month)
