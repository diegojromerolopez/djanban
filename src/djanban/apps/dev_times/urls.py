# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.dev_times import views as dev_time_views

app_name = "dev_times"

urlpatterns = [
    url(
        r"^daily_spent_time/?$",
        dev_time_views.view_daily_spent_times,
        name="view_daily_spent_times",
    ),
    url(
        r"^export_daily_spent_times/?$",
        dev_time_views.export_daily_spent_times,
        name="export_daily_spent_times",
    ),
    url(
        r"^send_daily_spent_times/?$",
        dev_time_views.send_daily_spent_times,
        name="send_daily_spent_times",
    ),
]
