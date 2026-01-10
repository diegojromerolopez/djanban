# -*- coding: utf-8 -*-

from django.urls import re_path as url, include

from djanban.apps.slideshow.views import view


app_name = 'slideshow'

urlpatterns = [
    url(r'^$', view, name="view"),
]
