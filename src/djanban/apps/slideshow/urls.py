# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djanban.apps.slideshow.views import view

urlpatterns = [
    url(r'^$', view, name="view"),
]
