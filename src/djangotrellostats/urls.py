# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from djangotrellostats.apps.public import views as public_views

urlpatterns = [
    url(r'^$', public_views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^member/', include('djangotrellostats.apps.members.urls', namespace="members")),
    url(r'^boards/', include('djangotrellostats.apps.boards.urls', namespace="boards")),
    url(r'^times/', include('djangotrellostats.apps.dev_times.urls', namespace="dev_times")),
    url(r'^charts/', include('djangotrellostats.apps.charts.urls', namespace="charts")),
    url(r'^hourly_rates/', include('djangotrellostats.apps.hourly_rates.urls', namespace="hourly_rates")),
]
