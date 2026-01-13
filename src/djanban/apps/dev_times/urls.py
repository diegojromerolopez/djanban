from django.urls import re_path

from djanban.apps.dev_times import views as dev_time_views

app_name = "dev_times"

urlpatterns = [
    re_path(
        r"^daily_spent_time/?$",
        dev_time_views.view_daily_spent_times,
        name="view_daily_spent_times",
    ),
    re_path(
        r"^export_daily_spent_times/?$",
        dev_time_views.export_daily_spent_times,
        name="export_daily_spent_times",
    ),
    re_path(
        r"^send_daily_spent_times/?$",
        dev_time_views.send_daily_spent_times,
        name="send_daily_spent_times",
    ),
]
