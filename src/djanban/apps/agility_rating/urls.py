from django.urls import path

from djanban.apps.agility_rating.views import delete, edit, new, view

app_name = "agility_rating"

urlpatterns = [
    path("", view, name="view"),
    path("new", new, name="new"),
    path("edit", edit, name="edit"),
    path("delete", delete, name="delete"),
]
