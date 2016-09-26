# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
from datetime import timedelta

import pygal
from django.db.models import Sum
from djangotrellostats.apps.dev_environment.models import Interruption


# Burndown for the board
def burndown(board, show_interruptions=False):

    chart_title = u"Burndown for board {0}".format(board.name)
    if show_interruptions:
        chart_title += u", including interruptions suffered by the team, "
    chart_title += u" as of {1}".format(board.name, board.get_human_fetch_datetime())

    burndown_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                print_zeroes=False, fill=False, human_readable=True, x_label_rotation=65)

    # Estimated number of hours
    estimated_number_of_hours = board.estimated_number_of_hours

    # Remaining hours
    remaining_time = estimated_number_of_hours
    daily_spent_times = board.daily_spent_times.filter(spent_time__gt=0).distinct().order_by("date")

    # Remaining time is neede for making the burndown chart
    if remaining_time is None:
        return burndown_chart.render_django_response()

    # Start working date in this board
    start_working_date = board.get_working_start_date()
    if start_working_date is None:
        return burndown_chart.render_django_response()

    # End working date in this board
    end_working_date = board.get_working_end_date()
    if end_working_date is None:
        return burndown_chart.render_django_response()

    # Remaining time values
    remaining_time_values = [remaining_time]

    # Dates where there is some work in this requirement
    x_labels = ["Start"]
    interruptions = []

    date_i = copy.deepcopy(start_working_date)
    remaining_time_i = copy.deepcopy(remaining_time)
    while date_i <= end_working_date:
        spent_time = daily_spent_times.filter(date=date_i).aggregate(
            spent_time_sum=Sum("spent_time")
        )["spent_time_sum"]

        if spent_time is not None and spent_time > 0:
            remaining_time_i -= spent_time
            remaining_time_values.append(remaining_time_i)
            x_labels.append(date_i.strftime("%Y-%m-%d"))

        # Interruptions
        if show_interruptions:
            num_interruptions = Interruption.objects.filter(datetime__date=date_i).count()
            if num_interruptions > 0:
                interruptions.append(num_interruptions)

        date_i += timedelta(days=1)

    burndown_chart.add(u"Initial estimation for {0}".format(board.name), [remaining_time for i in range(0, len(x_labels))])
    burndown_chart.x_labels = x_labels
    burndown_chart.add(u"Burndown of {0}".format(board.name), remaining_time_values)

    if show_interruptions:
        burndown_chart.add(u"Interruptions of {0}".format(board.name), interruptions)

    return burndown_chart.render_django_response()
