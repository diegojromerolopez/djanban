# -*- coding: utf-8 -*-
from django.urls import re_path as url, include

from djanban.apps.agility_rating.views import view, new, edit, delete


app_name = 'agility_rating'

urlpatterns = [
    url(r'^$', view, name="view"),
    url(r'^new$', new, name="new"),
    url(r'^edit$', edit, name="edit"),
    url(r'^delete$', delete, name="delete"),
]
