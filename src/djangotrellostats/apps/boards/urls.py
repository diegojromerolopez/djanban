# -*- coding: utf-8 -*-

from django.conf.urls import url

from djangotrellostats.apps.boards.views import boards
from djangotrellostats.apps.boards.views import workflows


urlpatterns = [
    url(r'^init-boards$', boards.init_boards, name="init_boards"),

    # Board URLs
    url(r'^my-boards$', boards.view_list, name="view_boards"),
    url(r'^(?P<board_id>\d+)/lists/?$', boards.view_lists, name="view_board_lists"),
    url(r'^(?P<board_id>\d+)/delete/?$', boards.delete, name="delete_board"),

    url(r'^(?P<board_id>\d+)/cards/?$', boards.view_card_report, name="view_card_report"),
    url(r'^(?P<board_id>\d+)/workflow_card_report/(?P<workflow_id>\d+)/?$', boards.view_workflow_card_report, name="view_workflow_card_report"),

    url(r'^(?P<board_id>\d+)/labels/?$', boards.view_label_report, name="view_label_report"),
    url(r'^(?P<board_id>\d+)/members/?$', boards.view_member_report, name="view_member_report"),

    url(r'^(?P<board_id>\d+)/fetch/?$', boards.fetch, name="fetch"),

    # Workflow URLs
    url(r'^(?P<board_id>\d+)/workflows/?$', workflows.view_list, name="view_workflows"),
    url(r'^(?P<board_id>\d+)/workflows/new/?$', workflows.new, name="new_workflow"),
    url(r'^(?P<board_id>\d+)/workflows/(?P<workflow_id>\d+)/edit/?$', workflows.edit, name="edit_workflow"),
    url(r'^(?P<board_id>\d+)/workflows/(?P<workflow_id>\d+)/delete/?$', workflows.delete, name="delete_workflow"),

    # Change list type
    url(r'^change-list-type/?$', boards.change_list_type, name="change_list_type"),


]