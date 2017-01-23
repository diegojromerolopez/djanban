# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from djangotrellostats.apps.api.views import boards, cards
from djangotrellostats.apps.journal.views import JournalEntryTagAutocompleteView


urlpatterns = [
    # Board API
    url(r'^boards/info/?$', boards.get_boards, name="get_boards"),
    url(r'^boards/(?P<board_id>\d+)/info/?$', boards.get_board, name="get_board"),

    # Card API
    url(r'^cards/(?P<board_id>\d+)/(?P<card_id>\d+)/info/?$', cards.get_card, name="get_card")
]