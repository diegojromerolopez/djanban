# -*- coding: utf-8 -*-

from django.urls import re_path as url, include

from djanban.apps.niko_niko_calendar.views import view_calendar, new_mood_measurement


app_name = 'niko_niko_calendar'

urlpatterns = [
    # View the niko-niko calendar
    url(r'^$', view_calendar, name="view_calendar"),
    # Create a new mood measurement
    url(r'^new_mood_measurement', new_mood_measurement, name="new_mood_measurement"),
]

