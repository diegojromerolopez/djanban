# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from djangotrellostats.apps.agility_rating.views import view, new, edit, delete

urlpatterns = [
    url(r'^$', view, name="view"),
    url(r'^new$', new, name="new"),
    url(r'^edit$', edit, name="edit"),
    url(r'^delete$', delete, name="delete"),
]
