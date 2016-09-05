# -*- coding: utf-8 -*-

from django.conf.urls import url, include


from djangotrellostats.apps.dev_environment.views import index
from djangotrellostats.apps.dev_environment.views import interruptions
from djangotrellostats.apps.dev_environment.views import noise_measurements


urlpatterns = [
    # Index
    url(r'^$', index.index, name="index"),
    url(r'^interruptions/?$', interruptions.view_list, name="view_interruptions"),
    url(r'^interruptions/new/?$', interruptions.new, name="new_interruption"),
    url(r'^interruptions/(?P<interruption_id>\d+)/delete/?$', interruptions.delete, name="delete_interruption"),

    url(r'^noise_measurements/?$', noise_measurements.view_list, name="view_noise_measurements"),
    url(r'^noise_measurements/new/?$', noise_measurements.new, name="new_noise_measurement"),
    url(r'^noise_measurements/(?P<noise_measurement_id>\d+)/delete/?$', noise_measurements.delete,
        name="delete_noise_measurement"),
]
