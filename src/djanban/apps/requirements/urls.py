from django.urls import path, re_path

from djanban.apps.requirements.views import view_list, new, view, edit, delete



app_name = 'requirements'

urlpatterns = [
    # List of requirements
    path('', view_list, name="view_requirements"),
    path('new', new, name="new_requirement"),
    re_path(r'^(?P<requirement_code>\w+)/view/?$', view, name="view_requirement"),
    re_path(r'^(?P<requirement_code>\w+)/edit/?$', edit, name="edit_requirement"),
    re_path(r'^(?P<requirement_code>\w+)/delete/?$', delete, name="delete_requirement"),
]