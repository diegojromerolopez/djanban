# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.charts.views import members


urlpatterns = [
    url(r'^task_forward_movements_by_member/(?P<board_id>[\d]+)?$', members.task_forward_movements_by_member, name="task_forward_movements_by_member"),
    url(r'^task_backward_movements_by_member/(?P<board_id>[\d]+)?$', members.task_backward_movements_by_member, name="task_backward_movements_by_member"),

    url(r'^spent_time_by_week/((?P<week_of_year>[\d]+)/)?(?P<board_id>[\d]+)?$', members.spent_time_by_week, name="spent_time_by_week"),
]
