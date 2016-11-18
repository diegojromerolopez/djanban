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

    url(r'^avg_spent_time_by_weekday/(?P<board_id>[\d]+)?$', private.avg_spent_time_by_weekday, name="avg_spent_time_by_weekday"),

    # Lead time
    url(r'^avg_lead_time/(?P<board_id>\d+)?$', private.avg_lead_time, name="avg_lead_time"),
    url(r'^avg_lead_time_by_month/(?P<board_id>\d+)?$', private.avg_lead_time_by_month, name="avg_lead_time_by_month"),

    # Cycle time
    url(r'^avg_cycle_time/(?P<board_id>[\d]+)?$', private.avg_cycle_time, name="avg_cycle_time"),
    url(r'^avg_cycle_time_by_month/(?P<board_id>\d+)?$', private.avg_cycle_time_by_month, name="avg_cycle_time_by_month"),

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

    # Time scatterplot
    url(
        r'^time_scatterplot/(?P<time_metric>lead_time|cycle_time|spent_time)/?$',
        private.time_scatterplot, name="time_scatterplot"
        ),
    url(
        r'^time_scatterplot/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/?$',
        private.time_scatterplot, name="time_scatterplot"
    ),
    url(
        r'^time_scatterplot/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/?$',
        private.time_scatterplot, name="time_scatterplot"
    ),
    url(
        r'^time_scatterplot/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',
        private.time_scatterplot, name="time_scatterplot"
    ),

    # Time box chart
    url(
        r'^time_box/(?P<time_metric>lead_time|cycle_time|spent_time)/?$',
        private.time_box, name="time_box"
    ),
    url(
        r'^time_box/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/?$',
        private.time_box, name="time_box"
    ),
    url(
        r'^time_box/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/?$',
        private.time_box, name="time_box"
    ),
    url(
        r'^time_box/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',
        private.time_box, name="time_box"
    ),

    # Lead/Cycle time vs. Spent time
    url(
        r'^time_vs_spent_time/(?P<time_metric>lead_time|cycle_time|spent_time)/?$',
        private.time_vs_spent_time, name="time_vs_spent_time"
    ),
    url(
        r'^time_vs_spent_time/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/?$',
        private.time_vs_spent_time, name="time_vs_spent_time"
    ),
    url(
        r'^time_vs_spent_time/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/?$',
        private.time_vs_spent_time, name="time_vs_spent_time"
    ),
    url(
        r'^time_vs_spent_time/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<board_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/?$',
        private.time_vs_spent_time, name="time_vs_spent_time"
    ),

    # Card age per list
    url(r'^card_age/(?P<board_id>\d+)/?$', private.card_age, name="card_age"),

    # Completion histogram
    url(r'^completion_histogram/(?P<board_id>\d+|all)/?$', private.completion_histogram, name="completion_histogram"),
    url(r'^completion_histogram/(?P<board_id>\d+|all)/(?P<time_metric>lead_time|cycle_time|spent_time)/?$',
        private.completion_histogram, name="completion_histogram"),
    url(r'^completion_histogram/(?P<board_id>\d+|all)/(?P<time_metric>lead_time|cycle_time|spent_time)/(?P<units>days|hours)/?$',
        private.completion_histogram, name="completion_histogram"),

    # Cumulative list evolution
    url(r'^cumulative_flow_diagram/(?P<board_id>\d+)(/(?P<day_step>[\d]+))?$', private.cumulative_flow_diagram,
        name="cumulative_list_evolution"),
    url(r'^cumulative_flow_diagram/(?P<board_id>\d+)(/(?P<day_step>[\d]+))?$', private.cumulative_flow_diagram,
        name="cumulative_flow_diagram"),

    url(r'^cumulative_list_type_evolution/(?P<board_id>\d+|all)(/(?P<day_step>[\d]+))?$', private.cumulative_list_type_evolution,
        name="cumulative_list_type_evolution"),

    url(r'^cumulative_card_evolution/(?P<board_id>\d+|all)(/(?P<day_step>[\d]+))?$', private.cumulative_card_evolution,
        name="cumulative_card_evolution"),

    # Evolution of number of comments
    url(r'^number_of_comments/?$',private.number_of_comments, name="number_of_comments"),
    url(r'^number_of_comments/(?P<board_id>[\d]+)/?$',private.number_of_comments, name="number_of_comments"),
    url(r'^number_of_comments/(?P<board_id>[\d]+)/(?P<card_id>[\d]+)/?$',private.number_of_comments, name="number_of_comments"),

    # Number of cards by member
    url(r'^number_of_cards_by_member/?$',private.number_of_cards_by_member, name="number_of_cards_by_member"),
    url(r'^number_of_cards_by_member/(?P<board_id>[\d]+)/?$',private.number_of_cards_by_member, name="number_of_cards_by_member"),

    # Spent time by member
    url(r'^spent_time_by_member/?$', private.spent_time_by_member, name="spent_time_by_member"),
    url(r'^spent_time_by_member/(?P<board_id>[\d]+)/?$', private.spent_time_by_member, name="spent_time_by_member"),

    # Total number of comments
    url(r'^number_of_comments_by_member/?$',private.number_of_comments_by_member, name="number_of_comments_by_member"),
    url(r'^number_of_comments_by_member/(?P<board_id>[\d]+)/?$',private.number_of_comments_by_member, name="number_of_comments_by_member"),
    url(r'^number_of_comments_by_member/(?P<board_id>[\d]+)/(?P<card_id>[\d]+)/?$',private.number_of_comments_by_member, name="number_of_comments_by_member"),

    url(r'^avg_time_by_list/(?P<board_id>\d+)/(?P<workflow_id>\d+)?/?$', private.avg_time_by_list, name="avg_time_by_list"),
    url(r'^avg_std_dev_time_by_list/(?P<board_id>[\d]+)/(?P<workflow_id>\d+)?/?$', private.avg_std_dev_time_by_list, name="avg_std_dev_time_by_list"),

    url(r'^public_avg_spent_times/(?P<board_public_access_code>.+)/?$', public.avg_spent_times, name="public_avg_spent_time"),
    url(r'^public_avg_estimated_times/(?P<board_public_access_code>.+)/?$', public.avg_estimated_times, name="public_avg_estimated_time"),
    url(r'^public_avg_time_by_list/(?P<board_public_access_code>.+)/?$', public.avg_time_by_list, name="public_avg_time_by_list"),

    url(r'^interruptions/(?P<board_id>\d+)?/?$', private.number_of_interruptions, name="interruptions"),
    url(r'^evolution_of_number_of_interruptions/(?P<board_id>\d+)?/?$', private.evolution_of_number_of_interruptions, name="evolution_of_interruptions"),

    url(r'^interruption_spent_time/(?P<board_id>\d+)?/?$', private.interruption_spent_time, name="interruption_spent_time"),
    url(r'^evolution_of_interruption_spent_time/(?P<board_id>\d+)?/?$', private.interruption_spent_time, name="evolution_of_interruption_spent_time"),

    url(r'^interruptions_by_month/(?P<board_id>\d+)?/?$', private.number_of_interruptions_by_month, name="interruptions_by_month"),
    url(r'^interruption_spent_time_by_month/(?P<board_id>\d+)?/?$', private.interruption_spent_time_by_month, name="interruption_spent_time_by_month"),

    url(r'^interruptions_by_member/?$', private.number_of_interruptions_by_member, name="interruptions_by_member"),
    url(r'^interruption_spent_time_by_member/?$', private.interruption_spent_time_by_member,
        name="interruption_spent_time_by_member"),

    url(r'^noise_levels/?$', private.noise_level, name="noise_level"),
    url(r'^noise_level_per_hour/?$', private.noise_level_per_hour, name="noise_level_per_hour"),
    url(r'^noise_level_per_weekday/?$', private.noise_level_per_weekday, name="noise_level_per_weekday"),
    url(r'^subjective_noise_levels/?$', private.subjective_noise_level, name="subjective_noise_level"),

    url(r'^number_of_code_errors/(?P<grouped_by>month|commit)/(?P<board_id>\d+)/(?P<language>php|python)?$', private.number_of_code_errors, name="number_of_code_errors"),
    url(r'^number_of_code_errors/(?P<grouped_by>month|commit)/(?P<board_id>\d+)/(?P<repository_id>\d+)/(?P<language>php|python)?$', private.number_of_code_errors, name="number_of_code_errors"),

    url(r'^number_of_code_errors_per_loc/(?P<grouped_by>month|commit)/(?P<board_id>\d+)/(?P<language>php|python)?$',
        private.number_of_code_errors_per_loc, name="number_of_code_errors_per_loc"),
    url(r'^number_of_code_errors_per_loc/(?P<grouped_by>month|commit)/(?P<board_id>\d+)/(?P<repository_id>\d+)/(?P<language>php|python)?$',
        private.number_of_code_errors_per_loc, name="number_of_code_errors_per_loc"),

    url(r'^view_agility_rating/(?P<board_id>\d+)/?$', private.view_agility_rating, name="view_agility_rating")
]
