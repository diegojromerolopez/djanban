from django.urls import include, path, re_path

from djanban.apps.boards.views import boards, cards
from djanban.apps.journal.views import JournalEntryTagAutocompleteView

app_name = "boards"

urlpatterns = [
    path("init-boards", boards.init_boards, name="init_boards"),
    # Board URLs
    path("new", boards.new, name="new"),
    path("sync", boards.sync, name="sync"),
    path("my-boards", boards.view_list, name="view_boards"),
    re_path(r"^dashboard/?$", boards.view_list, name="view_board_dashboard"),
    path(
        "my-archived-boards", boards.view_archived_boards, name="view_archived_boards"
    ),
    re_path(r"^panorama/?$", boards.view_board_panorama, name="view_board_panorama"),
    re_path(
        r"^(?P<board_public_access_code>.+)/public_view/?$",
        boards.public_view,
        name="public_view",
    ),
    re_path(r"^(?P<board_id>\d+)/view/?$", boards.view, name="view"),
    re_path(r"^(?P<board_id>\d+)/view/?$", boards.view, name="view_board"),
    re_path(r"^(?P<board_id>\d+)/edit/?$", boards.edit, name="edit"),
    re_path(
        r"^(?P<board_id>\d+)/identicon/?$", boards.view_identicon, name="view_identicon"
    ),
    re_path(
        r"^(?P<board_id>\d+)/identicon/(?P<width>\d+)/(?P<height>\d+)/?$",
        boards.view_identicon,
        name="view_identicon",
    ),
    re_path(
        r"^(?P<board_id>\d+)/create-default-labels/?$",
        boards.create_default_labels,
        name="create_default_labels",
    ),
    re_path(r"^(?P<board_id>\d+)/archive/?$", boards.archive, name="archive"),
    re_path(r"^(?P<board_id>\d+)/unarchive/?$", boards.unarchive, name="unarchive"),
    re_path(r"^(?P<board_id>\d+)/lists/?$", boards.view_lists, name="view_lists"),
    re_path(r"^(?P<board_id>\d+)/lists/new/?$", boards.new_list, name="new_list"),
    re_path(
        r"^(?P<board_id>\d+)/lists/(?P<list_id>\d+)/?$",
        boards.edit_list,
        name="edit_list",
    ),
    re_path(
        r"^(?P<board_id>\d+)/lists/(?P<list_id>\d+)/swap/?$",
        boards.swap_list,
        name="swap_list",
    ),
    re_path(
        r"^(?P<board_id>\d+)/lists/(?P<list_id>\d+)/position/?$",
        boards.edit_list_position,
        name="edit_list_position",
    ),
    re_path(r"^(?P<board_id>\d+)/delete/?$", boards.delete, name="delete"),
    re_path(
        r"^(?P<board_id>\d+)/week-summary/(?P<member_id>(all|\d+))/(?P<week_of_year>\d{4}W\d{1,2})/?$",
        cards.view_week_summary,
        name="view_week_summary",
    ),
    re_path(r"^(?P<board_id>\d+)/cards/?$", cards.view_report, name="view_card_report"),
    re_path(r"^(?P<board_id>\d+)/cards/new/?$", cards.new, name="new_card"),
    path("<int:board_id>/cards/<int:card_id>", cards.view, name="view_card"),
    path(
        "c/<int:board_id>/<str:card_uuid>",
        cards.view_short_url,
        name="view_card_short_url",
    ),
    # Download attachment
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/attachments/(?P<attachment_id>\d+)/?$",
        cards.download_attachment,
        name="download_attachment",
    ),
    # Move cards
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/move_forward/?$",
        cards.move_forward,
        name="move_card_forward",
    ),
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/move_backward/?$",
        cards.move_backward,
        name="move_card_backward",
    ),
    # Add spent/estimated time
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/add_spent_estimated_time/?$",
        cards.add_spent_estimated_time,
        name="add_spent_estimated_time",
    ),
    # Modify card labels
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/labels/?$",
        cards.change_labels,
        name="change_card_labels",
    ),
    # New comment
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/comments/new/?$",
        cards.add_comment,
        name="add_comment",
    ),
    # Delete comment
    re_path(
        r"^(?P<board_id>\d+)/cards/(?P<card_id>\d+)/comments/(?P<comment_id>\d+)/delete/?$",
        cards.delete_comment,
        name="delete_comment",
    ),
    re_path(
        r"^(?P<board_id>\d+)/cards/export/?$",
        cards.export_report,
        name="export_card_report",
    ),
    re_path(
        r"^(?P<board_id>\d+)/cards/export_detailed_report/?$",
        cards.export_detailed_report,
        name="export_detailed_report",
    ),
    re_path(
        r"^(?P<board_id>\d+)/workflow_card_report/(?P<workflow_id>\d+)/?$",
        boards.view_workflow_card_report,
        name="view_workflow_card_report",
    ),
    re_path(
        r"^(?P<board_id>\d+)/labels/?$",
        boards.view_label_report,
        name="view_label_report",
    ),
    re_path(
        r"^(?P<board_id>\d+)/label/(?P<label_id>\d+)?$",
        boards.edit_label,
        name="edit_label",
    ),
    re_path(
        r"^(?P<board_id>\d+)/members/?$",
        boards.view_member_report,
        name="view_member_report",
    ),
    re_path(r"^(?P<board_id>\d+)/fetch/?$", boards.fetch, name="fetch"),
    re_path(
        r"^(?P<board_id>\d+)/gantt-chart/?$",
        boards.view_gantt_chart,
        name="view_gantt_chart",
    ),
    # Workflow URLs
    path(
        "<int:board_id>/workflows/",
        include("djanban.apps.workflows.urls", namespace="workflows"),
    ),
    # Requirement URLs
    path(
        "<int:board_id>/requirements/",
        include("djanban.apps.requirements.urls", namespace="requirements"),
    ),
    # Recurrent cards
    path(
        "<int:board_id>/recurrent-cards/",
        include("djanban.apps.recurrent_cards.urls", namespace="recurrent_cards"),
    ),
    # Repositories for this board
    path(
        "<int:board_id>/repositories/",
        include("djanban.apps.repositories.urls", namespace="repositories"),
    ),
    # Agility rating of the project
    path(
        "<int:board_id>/agility-rating/",
        include("djanban.apps.agility_rating.urls", namespace="agility_rating"),
    ),
    # Journal entry tags autocomplete
    re_path(
        r"^journal-entry-tags/autocomplete/?$",
        JournalEntryTagAutocompleteView.as_view(create_field="name"),
        name="journal_entry-tag-autocomplete",
    ),
    # Journal entries of this board
    path(
        "<int:board_id>/journal/",
        include("djanban.apps.journal.urls", namespace="journal"),
    ),
    # Routing with catch-em-all pattern useful for allowing loading push-state URLs
    # Read https://www.metaltoad.com/blog/url-routing-decoupled-app-angular-2-and-django for more information.
    re_path(
        r"^dashboard/(?P<board_id>\d+)(/(?P<path>.*))?/$",
        boards.view_taskboard,
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<board_id>\d+)(/(?P<path>.*))?/$",
        boards.view_taskboard,
        name="view_dashboard",
    ),
    re_path(
        r"^dashboard/(?P<board_id>\d+)(/(?P<path>.*))?/$",
        boards.view_taskboard,
        name="view_taskboard",
    ),
]
