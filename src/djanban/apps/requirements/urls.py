# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.requirements.views import delete, edit, new, view, view_list

app_name = "requirements"

urlpatterns = [
    # List of requirements
    url(r"^$", view_list, name="view_requirements"),
    url(r"^new$", new, name="new_requirement"),
    url(r"^(?P<requirement_code>\w+)/view/?$", view, name="view_requirement"),
    url(r"^(?P<requirement_code>\w+)/edit/?$", edit, name="edit_requirement"),
    url(r"^(?P<requirement_code>\w+)/delete/?$", delete, name="delete_requirement"),
]
