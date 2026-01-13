from django.urls import path, re_path

from djanban.apps.workflows import views

app_name = "workflows"

urlpatterns = [
    path("", views.view_list, name="view_list"),
    re_path(r"^new/?$", views.new, name="new"),
    re_path(r"^(?P<workflow_id>\d+)/edit/?$", views.edit, name="edit"),
    re_path(r"^(?P<workflow_id>\d+)/delete/?$", views.delete, name="delete"),
]
