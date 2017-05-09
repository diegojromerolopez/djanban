# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djanban.apps.niko_niko_calendar.views import view_calendar, new_mood_measurement

urlpatterns = [
    # View the niko-niko calendar
    url(r'^$', view_calendar, name="view_calendar"),
    # Create a new mood measurement
    url(r'^new_mood_measurement', new_mood_measurement, name="new_mood_measurement"),
]

