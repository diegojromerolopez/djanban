from django.urls import re_path as url

from djanban.apps.fetch.views import fetch

app_name = "fetch"

urlpatterns = [
    url(r"^fetch$", fetch, name="fetch_boards"),
]
