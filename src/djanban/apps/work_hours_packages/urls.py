from django.urls import path, re_path

from djanban.apps.work_hours_packages.views import view_list, new, view, edit, delete, notify_completions



app_name = 'work_hours_packages'

urlpatterns = [
    # List of work hours packages
    path('', view_list, name="view_work_hours_packages"),
    path('', view_list, name="view_list"),
    path('new', new, name="new"),
    path('notify_completions', notify_completions, name="notify_completions"),
    re_path(r'^(?P<work_hours_package_id>\w+)/view/?$', view, name="view"),
    re_path(r'^(?P<work_hours_package_id>\w+)/edit/?$', edit, name="edit"),
    re_path(r'^(?P<work_hours_package_id>\w+)/delete/?$', delete, name="delete"),
]