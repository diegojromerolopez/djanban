# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy
from datetime import timedelta

import numpy
import pygal
from django.db.models import Min, Max, Avg
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards, get_user_team_mates
from djangotrellostats.apps.charts.models import CachedChart
from djangotrellostats.apps.dev_environment.models import NoiseMeasurement


# Noise level
from djangotrellostats.apps.members.models import Member


def noise_level(current_user):

    # Caching
    chart_uuid = "noise_measurements.noise_level-{0}".format(current_user.id)
    chart = CachedChart.get(board=None, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Average noise levels per day in db as of {0}".format(timezone.now())

    noise_measurement_filter = {"member__in": get_user_team_mates(current_user)}

    noise_measurements = NoiseMeasurement.objects.filter(**noise_measurement_filter).order_by("datetime")

    noise_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                             print_zeroes=False, x_label_rotation=65,
                             human_readable=True)

    start_datetime = noise_measurements.aggregate(min_date=Min("datetime"))["min_date"]
    end_datetime = noise_measurements.aggregate(max_date=Max("datetime"))["max_date"]
    if start_datetime is None or end_datetime is None:
        return noise_chart.render_django_response()

    end_date = end_datetime.date()

    noise_values = []
    days = []

    date_i = copy.deepcopy(start_datetime).date()
    while date_i <= end_date:
        date_noise_measurements = noise_measurements.filter(datetime__date=date_i)
        if date_noise_measurements.exists():
            noise_values.append(
                numpy.mean([noise_measurement.noise_level for noise_measurement in date_noise_measurements])
            )
            days.append(date_i.strftime("%Y-%m-%d"))

        date_i += timedelta(days=1)

    noise_chart.add("Average noise level by day", noise_values)
    noise_chart.x_labels = days

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=noise_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average, min and max noise level per hour
def noise_level_per_hour(current_user):
    # Caching
    chart_uuid = "noise_measurements.noise_level_per_hour-{0}".format(current_user.id)
    chart = CachedChart.get(board=None, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Noise levels per hour in db as of {0}".format(timezone.now())

    noise_measurement_filter = {"member__in": get_user_team_mates(current_user)}

    noise_measurements = NoiseMeasurement.objects.filter(**noise_measurement_filter).order_by("datetime")

    noise_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False, x_label_rotation=0,
                                           human_readable=True)

    noise_values = {"avg": [], "min": [], "max": []}
    hours = []
    hour_i = 0
    while hour_i < 24:
        noise_level_in_hour_i = noise_measurements.\
            filter(datetime__hour=hour_i).\
            aggregate(avg=Avg("noise_level"), max=Max("noise_level"), min=Min("noise_level"))

        if noise_level_in_hour_i["avg"] is not None:
            noise_values["avg"].append(noise_level_in_hour_i["avg"])
            noise_values["min"].append(noise_level_in_hour_i["min"])
            noise_values["max"].append(noise_level_in_hour_i["max"])

            hours.append(hour_i)
        hour_i += 1

    noise_chart.add("Avg noise level", noise_values["avg"])
    noise_chart.add("Min noise level", noise_values["min"])
    noise_chart.add("Max noise level", noise_values["max"])
    noise_chart.x_labels = hours

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=noise_chart.render(is_unicode=True))
    return chart.render_django_response()


# Average, min and max noise level per weekday
def noise_level_per_weekday(current_user):
    # Caching
    chart_uuid = "noise_measurements.noise_level_per_weekday-{0}".format(current_user.id)
    chart = CachedChart.get(board=None, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Noise levels per weekday in db as of {0}".format(timezone.now())

    noise_measurement_filter = {"member__in": get_user_team_mates(current_user)}

    noise_measurements = NoiseMeasurement.objects.filter(**noise_measurement_filter).order_by("datetime")

    noise_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                             print_zeroes=False, x_label_rotation=0,
                             human_readable=True)

    noise_values = {"avg": [], "min": [], "max": []}
    weekday_dict = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}
    weekdays = []
    weekday_i = 1
    while weekday_i < 7:
        noise_level_in_hour_i = noise_measurements. \
            filter(datetime__week_day=weekday_i). \
            aggregate(avg=Avg("noise_level"), max=Max("noise_level"), min=Min("noise_level"))

        if noise_level_in_hour_i["avg"] is not None:
            noise_values["avg"].append(noise_level_in_hour_i["avg"])
            noise_values["min"].append(noise_level_in_hour_i["min"])
            noise_values["max"].append(noise_level_in_hour_i["max"])

            weekdays.append(weekday_dict[weekday_i])
        weekday_i += 1

    noise_chart.add("Avg noise level", noise_values["avg"])
    noise_chart.add("Min noise level", noise_values["min"])
    noise_chart.add("Max noise level", noise_values["max"])
    noise_chart.x_labels = weekdays

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=noise_chart.render(is_unicode=True))
    return chart.render_django_response()


# Subjective noise level
def subjective_noise_level(current_user, month=None, year=None):

    # Caching
    chart_uuid = "noise_measurements.subjective_noise_level-{0}-{1}-{2}".format(
        current_user.id,
        month if month else "None",
        year if year else "None"
    )
    chart = CachedChart.get(board=None, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Subjective noise levels as of {0}".format(timezone.now())

    noise_measurement_filter = {"member__in": get_user_team_mates(current_user)}
    noise_measurements = NoiseMeasurement.objects.filter(**noise_measurement_filter).order_by("datetime")

    if month and year and 1 <= month <= 12:
        noise_measurements = noise_measurements.filter(datetime__month=month, datetime__year=year)

    noise_chart = pygal.Bar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False, human_readable=True, x_label_rotation=45 )

    subjective_noise_levels = dict(NoiseMeasurement.SUBJECTIVE_NOISE_LEVELS)
    for level_key, level_name in subjective_noise_levels.items():
        noise_chart.add(u"{0}".format(level_name), noise_measurements.filter(subjective_noise_level=level_key).count())

    chart = CachedChart.make(board=None, uuid=chart_uuid, svg=noise_chart.render(is_unicode=True))
    return chart.render_django_response()
