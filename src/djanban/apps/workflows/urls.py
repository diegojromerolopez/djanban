# -*- coding: utf-8 -*-

from django.urls import re_path as url, include

from djanban.apps.workflows import views


app_name = 'workflows'

urlpatterns = [
    url(r'^$', views.view_list, name="view_list"),
    url(r'^new/?$', views.new, name="new"),
    url(r'^(?P<workflow_id>\d+)/edit/?$', views.edit, name="edit"),
    url(r'^(?P<workflow_id>\d+)/delete/?$', views.delete, name="delete"),
]
