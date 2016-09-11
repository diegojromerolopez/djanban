# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.base.views import auth

urlpatterns = [
    url(r'^login/?$', auth.login, name="login"),
    url(r'^logout/?$', auth.logout, name="logout"),
]

