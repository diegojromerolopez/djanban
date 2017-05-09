# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from djanban.apps.multiboards.views import multiboards


urlpatterns = [
    url(r'^$', multiboards.view_list, name="list"),
    url(r'^$', multiboards.view_list, name="view_list"),
    url(r'^view_archived$', multiboards.view_archived_list, name="list_archived"),
    url(r'^view_archived$', multiboards.view_archived_list, name="view_archived"),
    url(r'^new$', multiboards.new, name="new"),
    url(r'^(?P<multiboard_id>\d+)/view/?$', multiboards.view, name="view"),
    url(r'^(?P<multiboard_id>\d+)/view_task_board/?$', multiboards.view_task_board, name="view_task_board"),
    url(r'^(?P<multiboard_id>\d+)/edit/?$', multiboards.edit, name="edit"),
    url(r'^(?P<multiboard_id>\d+)/leave/?$', multiboards.leave, name="leave"),
    #url(r'^(?P<multiboard_id>\d+)/archive/?$', multiboards.archive, name="archive"),
    #url(r'^(?P<multiboard_id>\d+)/unarchive/?$', multiboards.unarchive, name="unarchive"),
    url(r'^(?P<multiboard_id>\d+)/delete/?$', multiboards.delete, name="delete"),
]
