# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import TemplateView

from djangotrellostats.apps.members.views import auth, main, spent_time_factors

urlpatterns = [
    url(r'^signup/?$', auth.signup, name="signup"),
    url(r'^signup/local/?$', auth.local_signup, name="local_signup"),
    url(r'^signup/trello/?$', auth.trello_signup, name="trello_signup"),

    url(r'^reset_password/?$', auth.reset_password, name="reset_password"),
    url(r'^reset_password_success/?$', TemplateView.as_view(template_name="members/reset_password_success.html"),
        name="reset_password_success"),

    url(r'^new/?$', main.new, name="new"),
    url(r'^view_members/?$', main.view_members, name="view_members"),

    url(r'^(?P<member_id>\d+)/give_access/?$', main.give_access_to_member, name="give_access"),
    url(r'^(?P<member_id>\d+)/change_password/?$', main.change_password_to_member, name="change_password"),

    # Member profile
    url(r'^(?P<member_id>\d+)/edit/?$', main.edit_profile, name="edit_profile"),
    url(r'^(?P<member_id>\d+)/edit/trello/?$', main.edit_trello_member_profile, name="edit_trello_member_profile"),

    # Spent time factors
    url(r'^(?P<member_id>\d+)/spent_time_factors/?$', spent_time_factors.view_list, name="view_spent_time_factors"),
    url(r'^(?P<member_id>\d+)/spent_time_factors/add/?$', spent_time_factors.add, name="new_spent_time_factor"),
    url(r'^(?P<member_id>\d+)/spent_time_factors/(?P<spent_time_factor_id>\d+)/?$', spent_time_factors.edit, name="edit_spent_time_factor"),
    url(r'^(?P<member_id>\d+)/spent_time_factors/(?P<spent_time_factor_id>\d+)/delete/?$', spent_time_factors.delete, name="delete_spent_time_factor"),

]
