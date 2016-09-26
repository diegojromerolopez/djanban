# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.journal.views import view, new_entry, view_entry, edit_entry, delete_entry
from djangotrellostats.apps.journal.views import JournalEntryTagAutocompleteView

urlpatterns = [

    # View the journal for this project
    url(r'^$', view, name="view"),

    url(r'^new$', new_entry, name="new_entry"),

    # View entry of this journal
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\d\w-]+)/?$', view_entry, name="view_entry"),

    # Edit entry of this journal
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\w\d-]+)/edit/?$', edit_entry, name="edit_entry"),

    # Delete entry of this journal
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\w\d-]+)/delete/?$', delete_entry, name="delete_entry"),
]
