# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.base.views import auth

app_name = "base"

urlpatterns = [
    url(r"^login/?$", auth.login, name="login"),
    url(r"^logout/?$", auth.logout, name="logout"),
]
