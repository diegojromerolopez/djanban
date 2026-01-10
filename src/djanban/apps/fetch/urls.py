from django.urls import re_path as url, include

from djanban.apps.fetch.views import fetch


app_name = 'fetch'

urlpatterns = [
    url(r'^fetch$', fetch, name="fetch_boards"),
]
