# -*- coding: utf-8 -*-

import copy
from datetime import timedelta

import pygal
from django.db.models import Min, Max
from django.utils import timezone

from djangotrellostats.apps.dev_environment.models import NoiseMeasurement


# Noise level
def noise_level():
    chart_title = u"Noise levels in db as of {0}".format(timezone.now())

    noise_measurements = NoiseMeasurement.objects.all().order_by("datetime")

    noise_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False,
                                           human_readable=True)

    for noise_measurement in noise_measurements:
        datetime = noise_measurement.datetime
        member = noise_measurement.member
        noise_chart.add(u"{0} {1}".format(member.initials, datetime.strftime("%Y-%m-%d %H:%M:%S")), noise_measurement.noise_level)

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