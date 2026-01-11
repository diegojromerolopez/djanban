from django.urls import path

from djanban.apps.fetch.views import fetch

app_name = "fetch"

urlpatterns = [
    path("fetch", fetch, name="fetch_boards"),
]
