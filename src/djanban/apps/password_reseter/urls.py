# -*- coding: utf-8 -*-

from django.conf.urls import url

from djanban.apps.password_reseter import views

urlpatterns = [
    url(r'^request-reset-password/?$', views.request_password_reset, name="request_password_reset"),
    url(r'^reset-password/(?P<uuid>[\w\d-]+)/?$', views.reset_password, name="reset_password"),
]
