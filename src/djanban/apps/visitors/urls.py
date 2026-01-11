from django.urls import path, re_path

from djanban.apps.visitors.views.main import view_list, new, edit, delete



app_name = 'visitors'

urlpatterns = [
    path('', view_list, name="view_list"),
    path('new', new, name="new"),
    path('<int:visitor_id>/edit', edit, name="edit"),
    re_path(r'^(?P<visitor_id>\d+)/delete', delete, name="delete"),
]