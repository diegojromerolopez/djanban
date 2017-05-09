# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from djanban.apps.notifications import views


urlpatterns = [
    url(r'^mark_as_read', views.mark_as_read, name="mark_as_read"),

]
