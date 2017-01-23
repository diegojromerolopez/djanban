# -*- coding: utf-8 -*-

from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board, Card


def move_to_list(request, board_id, card_id, destination_list_id):
    pass


def get_card(request, board_id, card_id):
    try:
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    card = board.cards.get(id=card_id)

    comments_json = []
    for comment in card.comments.all().order_by("-creation_datetime"):
        comment_json = {
            "id": comment.id,
            "uuid": comment.uuid,
            "content": comment.content,
            "creation_datetime": comment.creation_datetime
        }
        comments_json.append(comment_json)

    card_json = {
        "id": card.id,
        "uuid": card.uuid,
        "name": card.name,
        "description": card.description,
        "url": reverse("boards:view_card", args=(card.board_id, card.id,)),
        "short_url": card.short_url,
        "position": card.position,
        "comments": comments_json
    }
    return JsonResponse(card_json)