from django.urls import path, re_path
from djanban.apps.multiboards.views import multiboards




app_name = 'multiboards'

urlpatterns = [
    path('', multiboards.view_list, name="list"),
    path('', multiboards.view_list, name="view_list"),
    path('view_archived', multiboards.view_archived_list, name="list_archived"),
    path('view_archived', multiboards.view_archived_list, name="view_archived"),
    path('new', multiboards.new, name="new"),
    re_path(r'^(?P<multiboard_id>\d+)/view/?$', multiboards.view, name="view"),
    re_path(r'^(?P<multiboard_id>\d+)/view_task_board/?$', multiboards.view_task_board, name="view_task_board"),
    re_path(r'^(?P<multiboard_id>\d+)/edit/?$', multiboards.edit, name="edit"),
    re_path(r'^(?P<multiboard_id>\d+)/leave/?$', multiboards.leave, name="leave"),
    #url(r'^(?P<multiboard_id>\d+)/archive/?$', multiboards.archive, name="archive"),
    #url(r'^(?P<multiboard_id>\d+)/unarchive/?$', multiboards.unarchive, name="unarchive"),
    re_path(r'^(?P<multiboard_id>\d+)/delete/?$', multiboards.delete, name="delete"),
]