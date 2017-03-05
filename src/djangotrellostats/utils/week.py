# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, date
from django.utils import timezone

from isoweek import Week


# Return the iso week of year of a date
def get_iso_week_of_year(date=None):
    if date is None:
        date = timezone.now().date()
    iso_calendar_date = date.isocalendar()
    week_of_year = iso_calendar_date[1]
    return week_of_year


def get_week_of_year(date=None):
    if date is None:
        date = timezone.now().date()
    week_of_year = get_iso_week_of_year(date=date)
    return u"{0}W{1}".format(date.year, week_of_year)


def get_weeks_of_year_since_one_year_ago(date=None):
    if date is None:
        now = timezone.now()
        date = now.date()
    week_of_year = get_week_of_year(date)
    weeks_of_year = [week_of_year]
    for i in range(1, 53):
        weeks_of_year.append(get_week_of_year(date - timedelta(days=7) * i))
    return weeks_of_year


# Number of weeks for a given year
def number_of_weeks_of_year(year):
    return int(date(year, 12, 31).strftime("%W"))


def start_of_week_of_year(week, year):
    week = Week(year, week)
    return week.monday()


def end_of_week_of_year(week, year):
    week = Week(year, week)
    return week.sunday()