# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.http import Http404
from django.http import JsonResponse

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board


@member_required
def get_boards(request):
    try:
        boards = get_user_boards(request.user)
    except Board.DoesNotExist:
        raise Http404

    response_json = []
    for board in boards:
        board_json = {
            "id": board.id,
            "uuid": board.uuid,
            "name": board.name,
            "description": board.description,
            "lists": []
        }
        response_json.append(board_json)

    return JsonResponse(response_json, safe=False)


@member_required
def get_board(request, board_id):
    try:
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    lists_json = []
    for list_ in board.lists.all().order_by("position"):
        list_json = {
            "id": list_.id,
            "name": list_.name,
            "uuid": list_.uuid,
            "type": list_.type,
            "position": list_.position
        }

        card_list = []
        for card in list_.cards.filter(is_closed=False).order_by("position")[:2]:
            card_json = {
                "id": card.id,
                "uuid": card.uuid,
                "name": card.name,
                "description": card.description,
                "url": card.url,
                "short_url": card.short_url,
                "is_closed": card.is_closed,
                "position": card.position
            }
            card_list.append(card_json)

        #list_json["cards"] = card_list

        lists_json.append(list_json)

    board_json = {
        "id": board.id,
        "uuid": board.uuid,
        "name": board.name,
        "description": board.description,
        "lists": lists_json
    }

    return JsonResponse(board_json)

