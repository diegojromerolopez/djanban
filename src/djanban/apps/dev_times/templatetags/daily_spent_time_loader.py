# -*- coding: utf-8 -*-

import inspect
from django import template
import datetime

from django.db.models import Sum

from djanban.apps.base.auth import get_user_boards
from djanban.apps.dev_times.models import DailySpentTime

register = template.Library()


@register.assignment_tag
def get_daily_spent_times(current_user, member=None, start_date=None, end_date=None, week=None, board=None):
    daily_spent_time_filter = {}

    # Member filter
    if member:
        daily_spent_time_filter["member_id"] = member.id

    # Week
    if week and int(week) > 0:
        daily_spent_time_filter["week_of_year"] = week

    # Start date
    if start_date:
        daily_spent_time_filter["date__gte"] = _get_date_from_str(start_date)

    # End date
    if end_date:
        daily_spent_time_filter["date__lte"] = _get_date_from_str(end_date)

    # Board
    if board and get_user_boards(current_user).filter(id=board.id).exists():
        daily_spent_time_filter["board_id"] = board.id

    # Daily Spent Times
    daily_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter).order_by("-date")

    return daily_spent_times


@register.filter
def total_spent_time(daily_spent_times):
    return daily_spent_times.aggregate(sum=Sum("spent_time"))["sum"]


@register.filter
def total_estimated_time(daily_spent_times):
    return daily_spent_times.aggregate(sum=Sum("estimated_time"))["sum"]


@register.filter
def total_value_amount(daily_spent_times):
    return daily_spent_times.aggregate(sum=Sum("rate_amount"))["sum"]


@register.filter
def total_adjusted_spent_time(daily_spent_times):
    return _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="spent_time")


@register.filter
def total_adjusted_value_amount(daily_spent_times):
    return _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="rate_amount")


@register.filter
def total_time_difference(daily_spent_times):
    spent_time_sum = daily_spent_times.aggregate(sum=Sum("spent_time"))["sum"]
    estimated_time_sum = daily_spent_times.aggregate(sum=Sum("estimated_time"))["sum"]
    if spent_time_sum and estimated_time_sum:
        return estimated_time_sum - spent_time_sum
    return None


# Return the value of the sum adjusted for each member
def _adjusted_daily_spent_time_attribute_sum(daily_spent_times, attribute="spent_time"):
    adjusted_value_sum = 0
    member_dict = {}
    for daily_spent_time in daily_spent_times:
        if not daily_spent_time.member_id in member_dict:
            member_dict[daily_spent_time.member_id] = daily_spent_time.member

        member = member_dict[daily_spent_time.member_id]

        adjusted_value_sum += member.adjust_daily_spent_time(daily_spent_time, attribute)

    return adjusted_value_sum


# Converts a (possibly) date string in Y-m-d format into a date object
def _get_date_from_str(date_str):
    # If the parameter is a date, return it as is
    if type(date_str) == datetime.date:
        return date_str

    # Otherwise, convert it to date
    date = None
    if date_str:
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            date = None
    return date