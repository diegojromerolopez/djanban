# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import calendar
import datetime
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http.response import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.template import loader, Context

from djangotrellostats.apps.base.auth import get_user_boards, user_is_member
from djangotrellostats.apps.boards.models import Label
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from django.template.loader import get_template


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

    # Start and end date of the interval of the spent times that will be exported
    start_date = spent_times["start_date"]
    end_date = spent_times["end_date"]
    board = spent_times["board"]

    # Board string that will be placed in the filename
    board_str = ""
    if board:
        board_str = (u"{0}-".format(board.name)).lower()

    # Creation of the HTTP response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}export-daily-spent-times-from-{1}-to-{2}.csv"'.format(
        board_str, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    csv_template = loader.get_template('daily_spent_times/csv.txt')
    replacements = Context({
        'spent_times': spent_times["all"],
    })
    response.write(csv_template.render(replacements))
    return response


# Export daily spent report in CSV format
@login_required
def send_daily_spent_times(request):
    if request.method != "POST":
        raise Http404

    current_user = request.user
    current_user_boards = get_user_boards(current_user)

    recipient_email = request.POST.get("email")
    if not re.match(r"[^@]+@[^@]+", recipient_email):
        return JsonResponse({"message": "Invalid email"})

    daily_spent_times_filter = {}

    # Start date
    start_date_str = request.POST.get("start_date")
    start_date = None
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            daily_spent_times_filter["date__gte"] = start_date
        except ValueError:
            start_date = None

    # End date
    end_date_str = request.POST.get("end_date")
    end_date = None
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            daily_spent_times_filter["date__lte"] = end_date
        except ValueError:
            end_date = None

    # Week
    week = request.POST.get('week') if request.POST.get('week') and request.POST.get('week') > 0 else None
    if week:
        daily_spent_times_filter["week"] = week

    # Label
    label = None
    board = None
    label_str = request.POST.get("label")
    matches = re.match(r"all_from_board_(?P<board_id>\d+)", label_str)
    if matches and current_user_boards.filter(id=matches.group("board_id")).exists():
        label = None
        board = current_user_boards.get(id=matches.group("board_id"))
        daily_spent_times_filter["board"] = board

    elif Label.objects.filter(id=label_str).exists():
        label = Label.objects.get(id=label_str)
        board = label.board
        daily_spent_times_filter["board"] = board
        daily_spent_times_filter["card__labels"] = label

    # Member
    member = None
    if user_is_member(current_user):
        current_user_members = Member.objects.filter(Q(boards__in=current_user_boards)|Q(id=current_user.member.id)).distinct()
    else:
        current_user_members = Member.objects.filter(boards__in=current_user_boards).distinct()
    if request.POST.get("member") and current_user_members.filter(id=request.POST.get("member")).exists():
        member = current_user_members.get(id=request.POST.get("member"))
        daily_spent_times_filter["member"] = member

    daily_spent_times = DailySpentTime.objects.filter(**daily_spent_times_filter)

    replacements = {
        "email": recipient_email,
        "daily_spent_times": daily_spent_times,
        "week": week,
        "start_date": start_date,
        "end_date": end_date,
        "label": label,
        "board": board,
        "member": member
    }

    report_subject = get_template('daily_spent_times/emails/send_daily_spent_times_subject.txt').render(replacements)

    txt_message = get_template("daily_spent_times/emails/send_daily_spent_times.txt").render(replacements)
    html_message = get_template("daily_spent_times/emails/send_daily_spent_times.html").render(replacements)

    csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})
    csv_file_name = "custom_report_for_{0}.csv".format(recipient_email)

    try:
        message = EmailMultiAlternatives(report_subject, txt_message, settings.EMAIL_HOST_USER, [recipient_email])
        message.attach_alternative(html_message, "text/html")
        message.attach(csv_file_name, csv_report, 'text/csv')
        message.send()

        if request.GET.get("ajax"):
            return JsonResponse({"message": "Spent times sent successfully"})
        return render(request, "daily_spent_times/send_daily_spent_times_ok.html", replacements)
    except Exception:
        if request.GET.get("ajax"):
            return JsonResponse({"message": "Error when sending data"}, status=500)
        return render(request, "daily_spent_times/send_daily_spent_times_error.html", replacements)


# Return the filtered queryset and the replacements given the GET parameters
def _get_daily_spent_times_replacements(request):

    selected_member_id = request.GET.get("member_id")
    selected_member = None
    if selected_member_id:
        selected_member = Member.objects.get(id=selected_member_id)

    spent_times = _get_daily_spent_times_from_request(request)

    replacements = {
        "member": request.user.member if user_is_member(request.user) else None,
        "boards": get_user_boards(request.user),
        "members": Member.objects.all()
    }

    # Start date
    start_date_str = request.GET.get("start_date")
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            replacements["start_date"] = start_date
            replacements["date_interval"] = [start_date, timezone.now().date()]
        except ValueError:
            start_date = None

    # End date
    end_date_str = request.GET.get("end_date")
    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            replacements["end_date"] = end_date
            replacements["date_interval"][1] = end_date
        except ValueError:
            end_date = None

    replacements["selected_member"] = selected_member

    # If we are filtering by board, filter by board_id
    label_id = request.GET.get("label_id", request.GET.get("label"))
    label = None
    board = None
    if label_id:
        matches = re.match(r"all_from_board_(?P<board_id>\d+)", label_id)
        if matches:
            board = get_user_boards(request.user).get(id=matches.group("board_id"))
            label = None
            replacements["selected_label"] = label
            replacements["label"] = label
            replacements["selected_board"] = board
            replacements["board"] = board
        else:
            boards = get_user_boards(request.user)
            label = Label.objects.get(board__in=boards, id=label_id)
            replacements["selected_label"] = label
            replacements["label"] = label
            replacements["selected_board"] = label.board
            replacements["board"] = label.board

    board_id = request.GET.get("board_id", request.GET.get("board"))
    if not label_id and board_id:
        board = get_user_boards(request.user).get(id=board_id)
        label = None
        replacements["selected_label"] = label
        replacements["label"] = label
        replacements["selected_board"] = board
        replacements["board"] = board

    daily_spent_times = spent_times["all"]
    replacements["week"] = request.GET.get('week') if request.GET.get('week') and request.GET.get('week') > 0 else None
    replacements["months"] = spent_times["per_month"]

    return {"queryset": daily_spent_times, "replacements": replacements}


# Return the daily spent times from a request
def _get_daily_spent_times_from_request(request):
    current_user = request.user
    selected_member = None
    if request.GET.get("member_id"):
        selected_member = Member.objects.get(id=request.GET.get("member_id"))

    spent_times = _get_daily_spent_times_queryset(current_user, selected_member,
                                                  request.GET.get("start_date"), request.GET.get("end_date"),
                                                  request.GET.get('week'),
                                                  request.GET.get("label_id"))

    return spent_times


# Return the filtered queryset and the replacements given the GET parameters
def _get_daily_spent_times_queryset(current_user, selected_member, start_date_, end_date_, week, label_id):
    daily_spent_time_filter = {}

    # Member filter
    if selected_member:
        daily_spent_time_filter["member_id"] = selected_member.id

    # Start date
    start_date = None
    if start_date_:
        try:
            start_date = datetime.datetime.strptime(start_date_, "%Y-%m-%d").date()
            daily_spent_time_filter["date__gte"] = start_date
        except ValueError:
            start_date = None

    # End date
    end_date = None
    if end_date_:
        try:
            end_date = datetime.datetime.strptime(end_date_, "%Y-%m-%d").date()
            daily_spent_time_filter["date__lte"] = end_date
        except ValueError:
            end_date = None

    # Week
    if week and int(week) > 0:
        daily_spent_time_filter["week_of_year"] = week

    # Label
    label = None
    board = None
    current_user_boards = get_user_boards(current_user)
    matches = re.match(r"all_from_board_(?P<board_id>\d+)", label_id)
    if matches and current_user_boards.filter(id=matches.group("board_id")).exists():
        label = None
        board = current_user_boards.get(id=matches.group("board_id"))
        daily_spent_time_filter["board"] = board

    elif Label.objects.filter(id=label_id, board__in=current_user_boards).exists():
        label = Label.objects.get(id=label_id)
        board = label.board
        daily_spent_time_filter["board"] = board
        daily_spent_time_filter["card__labels"] = label

    # Daily Spent Times
    daily_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).order_by("-date")
    months = []

    # Grouped by months
    if daily_spent_times.exists():
        if start_date is None:
            start_date = daily_spent_times.order_by("date")[0].date

        if end_date is None:
            end_date = daily_spent_times[0].date

        date_i = datetime.date(start_date.year, start_date.month, 1)
        while date_i <= end_date:
            month_index = date_i.month
            year = date_i.year
            month_name = calendar.month_name[month_index]
            daily_spent_times_in_month_i = daily_spent_times.filter(date__year=year, date__month=month_index).order_by(
                "date")

            first_weekday, number_of_days_in_month = calendar.monthrange(year, month_index)

            rate_amount_sum = daily_spent_times_in_month_i.aggregate(sum=Sum("rate_amount"))["sum"]
            adjusted_amount_sum = _adjusted_amount_sum(daily_spent_times_in_month_i)
            spent_time_sum =  daily_spent_times_in_month_i.aggregate(sum=Sum("spent_time"))["sum"]
            adjusted_spent_time_sum = _adjusted_spent_time_sum(daily_spent_times_in_month_i)
            estimated_time_sum = daily_spent_times_in_month_i.aggregate(sum=Sum("estimated_time"))["sum"]
            diff_time_sum = daily_spent_times_in_month_i.aggregate(sum=Sum("diff_time"))["sum"]

            month = {
                "daily_spent_times": daily_spent_times_in_month_i,
                "values": {
                    "first_day": datetime.date(year, month_index, 1).isoformat(),
                    "last_day": datetime.date(year, month_index, number_of_days_in_month).isoformat(),
                    "name": month_name,
                    "number": month_index,
                    "year": year,
                    "i": month_index,
                    "rate_amount_sum": float(rate_amount_sum) if rate_amount_sum else None,
                    "adjusted_amount_sum": float(adjusted_amount_sum) if adjusted_amount_sum else None,
                    "spent_time_sum": float(spent_time_sum) if spent_time_sum else None,
                    'adjusted_spent_time_sum': float(adjusted_spent_time_sum) if adjusted_spent_time_sum else None,
                    "estimated_time_sum": float(estimated_time_sum) if estimated_time_sum else None,
                    "diff_time_sum": float(diff_time_sum) if diff_time_sum else None
                }
            }
            months.append(month)
            date_i = (date_i + relativedelta(months=1))

    replacements = {
        "all": daily_spent_times, "per_month": months,
        "start_date": start_date, "end_date": end_date,
        "board": board
    }
    return replacements


# Computes the adjusted amount according to the factor each member has
def _adjusted_amount_sum(daily_spent_times):
    return _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="rate_amount")


# Computes the adjusted spent time according to the factor each member has
def _adjusted_spent_time_sum(daily_spent_times):
    return _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="spent_time")


# Computes the adjusted spent time according to the factor each member has
def _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="spent_time"):
    adjusted_value_sum = 0
    member_dict = {}
    for daily_spent_time in daily_spent_times:
        if not daily_spent_time.member_id in member_dict:
            member_dict[daily_spent_time.member_id] = daily_spent_time.member

        member = member_dict[daily_spent_time.member_id]

        adjusted_value_sum += member.adjust_daily_spent_time(daily_spent_time, attribute)

    return adjusted_value_sum
