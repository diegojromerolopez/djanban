# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.charts.views import private, public


urlpatterns = [

    url(r'^requirement_burndown(/(?P<board_id>\d+)/)?$', private.requirement_burndown, name="requirement_burndown"),
    url(r'^requirement_burndown/(?P<board_id>\d+)/(?P<requirement_code>\w+)/?$', private.requirement_burndown,
        name="requirement_burndown"),

    url(r'^public_requirement_burndown(/(?P<board_public_access_code>.+)/)?$', public.requirement_burndown,
        name="public_requirement_burndown"),
    url(r'^public_requirement_burndown/(?P<board_public_access_code>.+)/(?P<requirement_code>\w+)/?$',
        public.requirement_burndown,
        name="public_requirement_burndown"),

    url(r'^burndown/(?P<board_id>\d+)/?$', private.burndown, name="burndown"),
    url(r'^public_burndown/(?P<board_public_access_code>.+)/?$', public.burndown, name="public_burndown"),

    url(r'^task_forward_movements_by_member/(?P<board_id>[\d]+)?$', private.task_forward_movements_by_member, name="task_forward_movements_by_member"),
    url(r'^task_backward_movements_by_member/(?P<board_id>[\d]+)?$', private.task_backward_movements_by_member, name="task_backward_movements_by_member"),

    url(r'^public/task_forward_movements_by_member/(?P<board_public_access_code>.+)?$', public.task_forward_movements_by_member, name="public_task_forward_movements_by_member"),
    url(r'^public/task_backward_movements_by_member/(?P<board_public_access_code>.+)?$', public.task_backward_movements_by_member, name="public_task_backward_movements_by_member"),

    url(r'^spent_time_by_week_evolution/(?P<board_id>[\d]+)/?$', private.spent_time_by_week_evolution, name="spent_time_by_week_evolution"),
    url(r'^spent_time_by_week/?$', private.spent_time_by_week, name="spent_time_by_week"),
    url(r'^spent_time_by_week/(?P<week_of_year>\d{4}W\d{2})/?$', private.spent_time_by_week, name="spent_time_by_week"),
    url(r'^spent_time_by_week/(?P<week_of_year>\d{4}W\d{2})/(?P<board_id>[\d]+)/?$', private.spent_time_by_week, name="spent_time_by_week"),
    url(r'^public_spent_time_by_week/(?P<week_of_year>\d{4}W\d{2})/(?P<board_public_access_code>.+)/?$', public.spent_time_by_week, name="public_spent_time_by_week"),

    url(r'^spent_time_by_day_of_the_week/?$', private.spent_time_by_day_of_the_week, name="spent_time_by_day_of_the_week"),
    url(r'^spent_time_by_day_of_the_week/(?P<member_id>\d+)/?$', private.spent_time_by_day_of_the_week, name="spent_time_by_day_of_the_week"),
    url(r'^spent_time_by_day_of_the_week/(?P<member_id>\d+)/(?P<week_of_year>\d{4}W\d{2})/?$', private.spent_time_by_day_of_the_week, name="spent_time_by_day_of_the_week"),
    url(r'^spent_time_by_day_of_the_week/(?P<member_id>\d+)/(?P<week_of_year>\d{4}W\d{2})/(?P<board_id>[\d]+)/?$', private.spent_time_by_day_of_the_week, name="spent_time_by_day_of_the_week"),

    url(r'^avg_lead_time/(?P<board_id>[\d]+)?$', private.avg_lead_time, name="avg_lead_time"),
    url(r'^avg_cycle_time/(?P<board_id>[\d]+)?$', private.avg_cycle_time, name="avg_cycle_time"),

    url(r'^public_avg_lead_time/(?P<board_public_access_code>.+)/?$', public.avg_lead_time, name="public_avg_lead_time"),
    url(r'^public_avg_cycle_time/(?P<board_public_access_code>.+)/?$', public.avg_cycle_time, name="public_avg_cycle_time"),

    url(r'^avg_spent_times/(?P<board_id>[\d]+)?$', private.avg_spent_times, name="avg_spent_time"),
    url(r'^avg_spent_time_by_month/(?P<board_id>[\d]+)?$', private.avg_spent_time_by_month, name="avg_spent_time_by_month"),
    url(r'^avg_estimated_times/(?P<board_id>[\d]+)?$', private.avg_estimated_times, name="avg_estimated_time"),
    url(r'^avg_estimated_time_by_month/(?P<board_id>[\d]+)?$', private.avg_estimated_time_by_month,
        name="avg_estimated_time_by_month"),
    url(r'^number_of_cards_worked_on_by_month/(?P<board_id>[\d]+)?$', private.number_of_cards_worked_on_by_month,
        name="number_of_cards_worked_on_by_month"),

    url(r'^number_of_cards_worked_on_by_week/(?P<board_id>[\d]+)?$', private.number_of_cards_worked_on_by_week,
        name="number_of_cards_worked_on_by_week"),

    url(r'^cumulative_list_evolution/(?P<board_id>[\d]+)(/(?P<day_step>[\d]+))?$', private.cumulative_list_evolution,
        name="cumulative_list_evolution"),
    url(r'^cumulative_card_evolution/(?P<board_id>[\d]+)(/(?P<day_step>[\d]+))?$', private.cumulative_card_evolution,
        name="cumulative_card_evolution"),

    url(r'^avg_time_by_list/(?P<board_id>[\d]+)$', private.avg_time_by_list, name="avg_time_by_list"),
    url(r'^avg_estimated_time_by_list/(?P<board_id>[\d]+)$', private.avg_estimated_time_by_list, name="avg_estimated_time_by_list"),

    url(r'^public_avg_spent_times/(?P<board_public_access_code>.+)/?$', public.avg_spent_times, name="public_avg_spent_time"),
    url(r'^public_avg_estimated_times/(?P<board_public_access_code>.+)/?$', public.avg_estimated_times, name="public_avg_estimated_time"),
    url(r'^public_avg_time_by_list/(?P<board_public_access_code>.+)/?$', public.avg_time_by_list, name="public_avg_time_by_list"),

    url(r'^interruptions/(?P<board_id>\d+)?/?$', private.number_of_interruptions, name="interruptions"),
    url(r'^interruptions_by_month/(?P<board_id>\d+)?/?$', private.number_of_interruptions_by_month, name="interruptions_by_month"),
    url(r'^noise_levels/?$', private.noise_level, name="noise_level"),
    url(r'^subjective_noise_levels/?$', private.subjective_noise_level, name="subjective_noise_level"),

    url(r'^number_of_code_errors_by_month/(?P<board_id>\d+)/(?P<language>php)?$', private.number_of_code_errors_by_month, name="number_of_code_errors_by_month"),
    url(r'^number_of_code_errors_by_month/(?P<board_id>\d+)/(?P<language>python)?$', private.number_of_code_errors_by_month, name="number_of_code_errors_by_month"),

    url(r'^number_of_code_errors_per_loc_by_month/(?P<board_id>\d+)/(?P<language>php)?$',
        private.number_of_code_errors_per_loc_by_month, name="number_of_code_errors_per_loc_by_month"),
    url(r'^number_of_code_errors_per_loc_by_month/(?P<board_id>\d+)/(?P<language>python)?$',
        private.number_of_code_errors_per_loc_by_month, name="number_of_code_errors_per_loc_by_month"),
]
