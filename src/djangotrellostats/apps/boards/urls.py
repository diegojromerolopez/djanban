# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.boards.views import boards, cards
from djangotrellostats.apps.journal.views import JournalEntryTagAutocompleteView


urlpatterns = [
    url(r'^init-boards$', boards.init_boards, name="init_boards"),

    # Board URLs
    url(r'^new$', boards.new, name="new"),
    url(r'^my-boards$', boards.view_list, name="view_boards"),
    url(r'^(?P<board_public_access_code>.+)/public_view/?$', boards.public_view, name="public_view"),
    url(r'^(?P<board_id>\d+)/view/?$', boards.view, name="view"),
    url(r'^(?P<board_id>\d+)/edit/?$', boards.edit, name="edit"),
    url(r'^(?P<board_id>\d+)/lists/?$', boards.view_lists, name="view_lists"),
    url(r'^(?P<board_id>\d+)/delete/?$', boards.delete, name="delete"),

    url(r'^(?P<board_id>\d+)/cards/?$', cards.view_report, name="view_card_report"),
    url(r'^(?P<board_id>\d+)/cards/(?P<card_id>\d+)$', cards.view, name="view_card"),

    # Move cards
    url(r'^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/move_forward/?$', cards.move_forward, name="move_card_forward"),
    url(r'^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/move_backward/?$', cards.move_backward, name="move_card_backward"),
    # Add spent/estimated time
    url(r'^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/add_spent_estimated_time/?$', cards.add_spent_estimated_time, name="add_spent_estimated_time"),
    # New comment
    url(r'^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/comments/new/?$', cards.add_comment, name="add_comment"),

    url(r'^(?P<board_id>\d+)/export_card_report/?$', cards.export_report, name="export_card_report"),
    url(r'^(?P<board_id>\d+)/workflow_card_report/(?P<workflow_id>\d+)/?$', boards.view_workflow_card_report, name="view_workflow_card_report"),

    url(r'^(?P<board_id>\d+)/labels/?$', boards.view_label_report, name="view_label_report"),
    url(r'^(?P<board_id>\d+)/members/?$', boards.view_member_report, name="view_member_report"),

    url(r'^(?P<board_id>\d+)/fetch/?$', boards.fetch, name="fetch"),

    # Change list type
    url(r'^change-list-type/?$', boards.change_list_type, name="change_list_type"),

    # Workflow URLs
    url(r'^(?P<board_id>\d+)/workflows/', include('djangotrellostats.apps.workflows.urls', namespace="workflows")),

    # Requirement URLs
    url(r'^(?P<board_id>\d+)/requirements/', include('djangotrellostats.apps.requirements.urls', namespace="requirements")),

    # Repositories for this board
    url(r'^(?P<board_id>\d+)/repositories/', include('djangotrellostats.apps.repositories.urls', namespace="repositories")),

    # Agility rating of the project
    url(r'^(?P<board_id>\d+)/agility-rating/', include('djangotrellostats.apps.agility_rating.urls', namespace="agility_rating")),

    # Journal entry tags autocomplete
    url(r'^journal-entry-tags/autocomplete/?$', JournalEntryTagAutocompleteView.as_view(create_field='name'), name="journal_entry-tag-autocomplete"),

    # Journal entries of this board
    url(r'^(?P<board_id>\d+)/journal/', include('djangotrellostats.apps.journal.urls', namespace="journal")),
]
