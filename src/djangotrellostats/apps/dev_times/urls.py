# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.dev_times import views as dev_time_views


urlpatterns = [
    url(r'^daily_spent_time/?$', dev_time_views.view_daily_spent_times, name="view_daily_spent_times")
]
