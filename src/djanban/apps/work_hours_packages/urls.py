# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djanban.apps.work_hours_packages.views import view_list, new, view, edit, delete, notify_completions

urlpatterns = [
    # List of work hours packages
    url(r'^$', view_list, name="view_work_hours_packages"),
    url(r'^$', view_list, name="view_list"),
    url(r'^new$', new, name="new"),
    url(r'^notify_completions$', notify_completions, name="notify_completions"),
    url(r'^(?P<work_hours_package_id>\w+)/view/?$', view, name="view"),
    url(r'^(?P<work_hours_package_id>\w+)/edit/?$', edit, name="edit"),
    url(r'^(?P<work_hours_package_id>\w+)/delete/?$', delete, name="delete"),
]