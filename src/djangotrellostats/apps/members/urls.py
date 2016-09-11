# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView

from djangotrellostats.apps.members.views import auth, main

urlpatterns = [
    url(r'^signup/?$', auth.signup, name="signup"),
    url(r'^reset_password/?$', auth.reset_password, name="reset_password"),
    url(r'^reset_password_success/?$', TemplateView.as_view(template_name="members/reset_password_success.html"),
        name="reset_password_success"),
    url(r'^view_members/?$', main.view_members, name="view_members"),
    url(r'^give_access/(?P<member_id>\d+)?$', main.give_access_to_member, name="give_access"),
    url(r'^change_password/(?P<member_id>\d+)?$', main.change_password_to_member, name="change_password"),
    url(r'^edit_profile/(?P<member_id>\d+)/??$', main.edit_profile, name="edit_profile"),
]