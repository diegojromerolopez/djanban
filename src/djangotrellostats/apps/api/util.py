# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re

from django.db import transaction
from django.http import Http404
from django.http import HttpResponseBadRequest
from django.http import JsonResponse

from djangotrellostats.apps.api.serializers import serialize_card
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board, Card, CardComment, List
from djangotrellostats.trello_api.cards import set_name, set_description


# Returns the card with id card_id
# if this is not a user's card or doesn't exist, raise 404.
def get_card_or_404(request, board_id, card_id):
    try:
        board = get_board_or_404(request, board_id)
        return board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist):
        raise Http404


# Returns the list with id equals to list_id
# if the list does not belong to the board with board_id or it does not exist (or is closed)
# raises a 404 error.
def get_list_or_404(request, board_id, list_id):
    try:
        board = get_board_or_404(request, board_id)
        return board.active_lists.get(id=list_id)
    except (Board.DoesNotExist, List.DoesNotExist):
        raise Http404


# Returns the board with id board_id
# if this is not a user's board or it doesn't exist, raise 404.
def get_board_or_404(request, board_id):
    try:
        return get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404