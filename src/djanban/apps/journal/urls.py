from django.urls import path, re_path

from djanban.apps.journal.views import (
    delete_entry,
    edit_entry,
    new_entry,
    view,
    view_entry,
)

app_name = "journal"

urlpatterns = [
    # View the journal for this project
    path("", view, name="view"),
    path("new", new_entry, name="new_entry"),
    # View entry of this journal
    re_path(
        r"^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\d\w-]+)/?$",
        view_entry,
        name="view_entry",
    ),
    # Edit entry of this journal
    re_path(
        r"^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\w\d-]+)/edit/?$",
        edit_entry,
        name="edit_entry",
    ),
    # Delete entry of this journal
    re_path(
        r"^(?P<year>\d+)/(?P<month>\d+)/(?P<journal_entry_slug>[\w\d-]+)/delete/?$",
        delete_entry,
        name="delete_entry",
    ),
]
