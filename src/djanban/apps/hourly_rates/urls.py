# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.hourly_rates import views as hourly_rate_views

app_name = "hourly_rates"

urlpatterns = [
    url(r"^$", hourly_rate_views.view_list, name="view_hourly_rates"),
    url(r"^new/?$", hourly_rate_views.new, name="new"),
    url(r"^(?P<hourly_rate_id>\d+)/edit/?$", hourly_rate_views.edit, name="edit"),
    url(r"^(?P<hourly_rate_id>\d+)/delete/?$", hourly_rate_views.delete, name="delete"),
]
