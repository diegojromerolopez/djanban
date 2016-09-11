# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.visitors.views.main import view_list, new, edit, delete

urlpatterns = [
    url(r'^$', view_list, name="view_list"),
    url(r'^new$', new, name="new"),
    url(r'^(?P<visitor_id>\d+)/edit$', edit, name="edit"),
    url(r'^(?P<visitor_id>\d+)/delete', delete, name="delete"),
]
