# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.password_reseter import views


app_name = 'password_reseter'

urlpatterns = [
    url(r'^request-reset-password/?$', views.request_password_reset, name="request_password_reset"),
    url(r'^reset-password/(?P<uuid>[\w\d-]+)/?$', views.reset_password, name="reset_password"),
]
