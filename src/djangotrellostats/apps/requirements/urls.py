# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.requirements.views import view_list, new, view, edit, delete

urlpatterns = [
    # List of requirements
    url(r'^$', view_list, name="view_requirements"),
    url(r'^new$', new, name="new_requirement"),
    url(r'^(?P<requirement_code>\w+)/view/?$', view, name="view_requirement"),
    url(r'^(?P<requirement_code>\w+)/edit/?$', edit, name="edit_requirement"),
    url(r'^(?P<requirement_code>\w+)/delete/?$', delete, name="delete_requirement"),
]