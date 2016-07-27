# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.workflows import views

urlpatterns = [
    url(r'^workflows/?$', views.view_list, name="view_list"),
    url(r'^workflows/new/?$', views.new, name="new"),
    url(r'^workflows/(?P<workflow_id>\d+)/edit/?$', views.edit, name="edit"),
    url(r'^workflows/(?P<workflow_id>\d+)/delete/?$', views.delete, name="delete"),
]
