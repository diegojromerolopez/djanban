# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from djangotrellostats.apps.api.views import boards, cards
from djangotrellostats.apps.journal.views import JournalEntryTagAutocompleteView


urlpatterns = [
    # Board API
    url(r'^boards/info/?$', boards.get_boards, name="get_boards"),

    url(r'^board/(?P<board_id>\d+)/info/?$', boards.get_board, name="get_board"),

    # Card API
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/info/?$', cards.get_card, name="get_card"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/?$', cards.add_new_comment, name="add_new_comment"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/comment/(?P<comment_id>\d+)/?$', cards.modify_comment, name="modify_comment"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/list/?$', cards.move_to_list, name="move_to_list"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/labels/?$', cards.change_labels, name="change_labels"),
    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/members/?$', cards.change_members, name="change_members"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/time/?$', cards.add_se_time, name="add_se_time"),

    url(r'^board/(?P<board_id>\d+)/card/(?P<card_id>\d+)/?$', cards.change, name="change"),
]
