# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.async_include import views

urlpatterns = [
    # Load
    url(r'^get/?$', views.get_template, name="get_template"),
]