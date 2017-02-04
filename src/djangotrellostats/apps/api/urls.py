# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from djangotrellostats.apps.api.views import boards, cards, lists, members
from djangotrellostats.apps.journal.views import JournalEntryTagAutocompleteView


urlpatterns = [
    # Members API
    url(r'^members/info/?$', members.get_members, name="get_members"),

    # Board API
    url(r'^boards/info/?$', boards.get_boards, name="get_boards"),
    url(r'^board/(?P<board_id>\d+)/info/?$', boards.get_board, name="get_board"),
    url(r'^board/(?P<board_id>\d+)/member/?$', boards.add_member, name="add_member"),
    url(r'^board/(?P<board_id>\d+)/member/(?P<member_id>\d+)/?$', boards.remove_member, name="remove_member"),

    # List API
    url(r'^board/(?P<board_id>\d+)/list/(?P<list_id>\d+)?$', lists.move_list, name="move_list"),

    # Card API
    url(r'^board/(?P<board_id>\d+)/card/?$', cards.add_card, name="add_card"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/info/?$', cards.get_card, name="get_card"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/?$', cards.add_new_comment, name="add_new_comment"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/(?P<comment_id>\d+)/?$', cards.modify_comment, name="modify_comment"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/list/?$', cards.move_to_list, name="move_to_list"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/labels/?$', cards.change_labels, name="change_labels"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/members/?$', cards.change_members, name="change_members"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/time/?$', cards.add_se_time, name="add_se_time"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/?$', cards.change, name="change"),

    # Blocking cards
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/blocking_card/?$', cards.add_blocking_card, name="add_blocking_card"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/blocking_card/(?P<blocking_card_id>\d+)?$', cards.remove_blocking_card, name="remove_blocking_card"),

    # Reviews
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/review/?$', cards.add_new_review, name="add_new_review"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/review/(?P<review_id>\d+)/?$', cards.delete_review, name="delete_review"),

    # Requirements
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/requirement/?$', cards.add_requirement, name="add_requirement"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/requirement/(?P<requirement_id>\d+)/?$', cards.remove_requirement, name="remove_requirement"),
]
