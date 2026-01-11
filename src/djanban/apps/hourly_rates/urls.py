from django.urls import path, re_path

from djanban.apps.hourly_rates import views as hourly_rate_views

app_name = "hourly_rates"

urlpatterns = [
    path("", hourly_rate_views.view_list, name="view_hourly_rates"),
    re_path(r"^new/?$", hourly_rate_views.new, name="new"),
    re_path(r"^(?P<hourly_rate_id>\d+)/edit/?$", hourly_rate_views.edit, name="edit"),
    re_path(
        r"^(?P<hourly_rate_id>\d+)/delete/?$", hourly_rate_views.delete, name="delete"
    ),
]
