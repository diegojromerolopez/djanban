# -*- coding: utf-8 -*-

from django.conf.urls import url
from djangotrellostats.apps.members.views import auth, main

urlpatterns = [
    url(r'^signup/?$', auth.signup, name="signup"),
    url(r'^login/?$', auth.login, name="login"),
    url(r'^logout/?$', auth.logout, name="logout"),
    url(r'^view_members/?$', main.view_members, name="view_members"),
    url(r'^give_access/(?P<member_id>\d+)?$', main.give_access_to_member, name="give_access"),
]