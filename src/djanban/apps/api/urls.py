from django.urls import re_path
from djanban.apps.api.views import boards, cards, lists, members
from djanban.apps.journal.views import JournalEntryTagAutocompleteView




app_name = 'api'

urlpatterns = [
    # Members API
    re_path(r'^members/info/?$', members.get_members, name="get_members"),

    # Board API
    re_path(r'^boards/info/?$', boards.get_boards, name="get_boards"),
    re_path(r'^board/(?P<board_id>\d+)/info/?$', boards.get_board, name="get_board"),
    re_path(r'^board/(?P<board_id>\d+)/member/?$', boards.add_member, name="add_member"),
    re_path(r'^board/(?P<board_id>\d+)/member/(?P<member_id>\d+)/?$', boards.remove_member, name="remove_member"),

    # List API
    re_path(r'^board/(?P<board_id>\d+)/list/(?P<list_id>\d+)?$', lists.move_list, name="move_list"),

    # Card API
    re_path(r'^board/(?P<board_id>\d+)/card/?$', cards.modify_cards, name="modify_cards"),

    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/info/?$', cards.get_card, name="get_card"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/?$', cards.add_new_comment, name="add_new_comment"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/(?P<comment_id>\d+)/?$', cards.modify_comment, name="modify_comment"),

    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/list/?$', cards.move_to_list, name="move_to_list"),

    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/labels/?$', cards.change_labels, name="change_labels"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/members/?$', cards.change_members, name="change_members"),

    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/forecasts/?$', cards.update_forecasts, name="update_forecasts"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/time/?$', cards.add_se_time, name="add_se_time"),

    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/?$', cards.change, name="change"),

    # File uploading
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/attachment/add/?$', cards.add_attachment, name="add_attachment"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/attachment/(?P<attachment_id>\d+)/?$', cards.delete_attachment, name="delete_attachment"),

    # Blocking cards
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/blocking_card/?$', cards.add_blocking_card, name="add_blocking_card"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/blocking_card/(?P<blocking_card_id>\d+)?$', cards.remove_blocking_card, name="remove_blocking_card"),

    # Reviews
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/review/?$', cards.add_new_review, name="add_new_review"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/review/(?P<review_id>\d+)/?$', cards.delete_review, name="delete_review"),

    # Requirements
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/requirement/?$', cards.add_requirement, name="add_requirement"),
    re_path(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/requirement/(?P<requirement_id>\d+)/?$', cards.remove_requirement, name="remove_requirement"),
]