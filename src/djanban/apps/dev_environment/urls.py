from django.urls import path, re_path

from djanban.apps.dev_environment.views import index, interruptions, noise_measurements

app_name = "dev_environment"

urlpatterns = [
    # Index
    path("", index.index, name="index"),
    re_path(r"^interruptions/?$", interruptions.view_list, name="view_interruptions"),
    re_path(r"^interruptions/new/?$", interruptions.new, name="new_interruption"),
    re_path(
        r"^interruptions/(?P<interruption_id>\d+)/delete/?$",
        interruptions.delete,
        name="delete_interruption",
    ),
    re_path(
        r"^noise_measurements/?$",
        noise_measurements.view_list,
        name="view_noise_measurements",
    ),
    re_path(
        r"^noise_measurements/new/?$",
        noise_measurements.new,
        name="new_noise_measurement",
    ),
    re_path(
        r"^noise_measurements/(?P<noise_measurement_id>\d+)/delete/?$",
        noise_measurements.delete,
        name="delete_noise_measurement",
    ),
]
