# -*- coding: utf-8 -*-

import copy
from datetime import timedelta

import numpy
import pygal
from django.db.models import Min, Max, Avg
from django.utils import timezone

from djangotrellostats.apps.dev_environment.models import NoiseMeasurement


# Noise level
def noise_level():
    chart_title = u"Average noise levels per day in db as of {0}".format(timezone.now())

    noise_measurements = NoiseMeasurement.objects.all().order_by("datetime")

    noise_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False, x_label_rotation=65,
                                           human_readable=True)

    start_datetime = noise_measurements.aggregate(min_date=Min("datetime"))["min_date"]
    end_datetime = noise_measurements.aggregate(max_date=Max("datetime"))["max_date"]
    if start_datetime is None or end_datetime is None:
        return noise_chart.render_django_response()

    noise_values = []
    days = []

    datetime_i = copy.deepcopy(start_datetime)
    while datetime_i <= end_datetime:
        date_noise_measurements = noise_measurements.filter(datetime__date=datetime_i.date())
        if date_noise_measurements.exists():
            noise_values.append(numpy.mean([noise_measurement.noise_level for noise_measurement in date_noise_measurements]))
            days.append(datetime_i.strftime("%Y-%m-%d"))

        datetime_i += timedelta(days=1)

    noise_chart.add("Average noise level by day", noise_values)
    noise_chart.x_labels = days

    return noise_chart.render_django_response()


# Average, min and max noise level per hour
def noise_level_per_hour():
    chart_title = u"Noise levels per hour in db as of {0}".format(timezone.now())

    noise_measurements = NoiseMeasurement.objects.all().order_by("datetime")

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
    return noise_chart.render_django_response()


# Average, min and max noise level per weekday
def noise_level_per_weekday():
    chart_title = u"Noise levels per weekday in db as of {0}".format(timezone.now())

    noise_measurements = NoiseMeasurement.objects.all().order_by("datetime")

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
    return noise_chart.render_django_response()

# Subjective noise level
def subjective_noise_level(month=None, year=None):
    chart_title = u"Subjective noise levels as of {0}".format(timezone.now())

    noise_measurements = NoiseMeasurement.objects.all().order_by("datetime")

    if month and year and 1 <= month <= 12:
        noise_measurements = noise_measurements.filter(datetime__month=month, datetime__year=year)

    noise_chart = pygal.Bar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False, human_readable=True, x_label_rotation=45 )

    subjective_noise_levels = dict(NoiseMeasurement.SUBJECTIVE_NOISE_LEVELS)
    for level_key, level_name in subjective_noise_levels.items():
        noise_chart.add(u"{0}".format(level_name), noise_measurements.filter(subjective_noise_level=level_key).count())

    return noise_chart.render_django_response()