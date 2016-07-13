# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.charts.views import members, cards, labels


urlpatterns = [
    url(r'^task_forward_movements_by_member/(?P<board_id>[\d]+)?$', members.task_forward_movements_by_member, name="task_forward_movements_by_member"),
    url(r'^task_backward_movements_by_member/(?P<board_id>[\d]+)?$', members.task_backward_movements_by_member, name="task_backward_movements_by_member"),
    url(r'^spent_time_by_week/((?P<week_of_year>[\d]+)/)?(?P<board_id>[\d]+)?$', members.spent_time_by_week, name="spent_time_by_week"),

    url(r'^avg_lead_time/(?P<board_id>[\d]+)?$', cards.avg_lead_time, name="avg_lead_time"),
    url(r'^avg_cycle_time/(?P<board_id>[\d]+)?$', cards.avg_cycle_time, name="avg_cycle_time"),

    url(r'^avg_spent_times/(?P<board_id>[\d]+)?$', labels.avg_spent_times, name="avg_spent_time"),
    url(r'^avg_estimated_times/(?P<board_id>[\d]+)?$', labels.avg_estimated_times, name="avg_estimated_time"),
    url(r'^avg_time_by_list/(?P<board_id>[\d]+)$', cards.avg_time_by_list, name="avg_time_by_list"),
]
