from django.conf.urls import url, include

from djangotrellostats.apps.fetch.views import fetch

urlpatterns = [
    url(r'^fetch$', fetch, name="fetch_boards"),
]