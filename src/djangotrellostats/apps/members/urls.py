# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.boards.views import boards
from djangotrellostats.apps.members.views import auth

urlpatterns = [
    url(r'^signup/?$', auth.signup, name="signup"),
    url(r'^login/?$', auth.login, name="login"),
    url(r'^logout/?$', auth.logout, name="logout"),
]