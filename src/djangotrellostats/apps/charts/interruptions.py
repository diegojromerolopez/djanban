# -*- coding: utf-8 -*-

import copy
from datetime import timedelta

import pygal
from django.db.models import Min, Max
from django.utils import timezone

from djangotrellostats.apps.dev_environment.models import Interruption


# Number of interruptions
def number_of_interruptions(board):
    chart_title = u"Number of interruptions as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    interruptions_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False,
                                          human_readable=True)

    interruptions_filter = {}
    if board:
        interruptions_filter["board"] = board

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")
    if not interruptions.exists():
        return interruptions_chart.render_django_response()

    min_datetime = interruptions.aggregate(min_datetime=Min("datetime"))["min_datetime"]
    max_datetime = interruptions.aggregate(max_datetime=Max("datetime"))["max_datetime"]

    date_i = copy.deepcopy(min_datetime.date())
    max_date = max_datetime.date() + timedelta(days=2)

    while date_i <= max_date:
        num_interruptions = interruptions.filter(datetime__date=date_i).count()

        if num_interruptions > 0:
            interruptions_chart.add(u"{0}".format(date_i.strftime("%Y-%m-%d")), num_interruptions)
        date_i += timedelta(days=1)

    return interruptions_chart.render_django_response()


# Number of interruptions by month
def number_of_interruptions_by_month(board):
    chart_title = u"Number of interruptions by month as of {0}".format(timezone.now())
    if board:
        chart_title += u" for board {0} as of {1}".format(board.name, board.get_human_fetch_datetime())

    interruptions_filter = {}
    if board:
        interruptions_filter["board"] = board

    interruptions = Interruption.objects.filter(**interruptions_filter).order_by("datetime")

    interruptions_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                                    print_zeroes=False,
                                                    human_readable=True)

    datetime_i = copy.deepcopy(interruptions.aggregate(min_datetime=Min("datetime"))["min_datetime"])
    if datetime_i is None:
        return interruptions_chart.render_django_response()

    date_i = datetime_i.date()
    month_i = date_i.month
    year_i = date_i.year
    first_loop = True
    monthly_measurement = None
    while first_loop or (monthly_measurement is not None and monthly_measurement > 0):
        first_loop = False
        monthly_interruptions = interruptions.filter(datetime__month=month_i, datetime__year=year_i)
        monthly_measurement = monthly_interruptions.count()
        # For each month that have some data, add it to the chart
        if monthly_measurement > 0:
            interruptions_chart.add(u"On {0}-{1}".format(year_i, month_i), monthly_measurement)

            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

    return interruptions_chart.render_django_response()