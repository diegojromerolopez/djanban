from django.urls import re_path

from djanban.apps.password_reseter import views

app_name = "password_reseter"

urlpatterns = [
    re_path(
        r"^request-reset-password/?$",
        views.request_password_reset,
        name="request_password_reset",
    ),
    re_path(
        r"^reset-password/(?P<uuid>[\w\d-]+)/?$",
        views.reset_password,
        name="reset_password",
    ),
]
