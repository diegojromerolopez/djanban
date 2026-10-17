# -*- coding: utf-8 -*-


from django.urls import re_path as url

from djanban.apps.notifications import views

app_name = "notifications"

urlpatterns = [
    url(r"^mark_as_read", views.mark_as_read, name="mark_as_read"),
]
