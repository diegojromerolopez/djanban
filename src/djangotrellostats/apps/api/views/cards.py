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
        author = comment.author
        comment_json = {
            "id": comment.id,
            "uuid": comment.uuid,
            "content": comment.content,
            "creation_datetime": comment.creation_datetime,
            "author": {"id": author.id, "trello_username": author.trello_username, "initials": author.initials}
        }
        comments_json.append(comment_json)

    card_json = {
        "id": card.id,
        "uuid": card.uuid,
        "name": card.name,
        "description": card.description,
        "local_url": reverse("boards:view_card", args=(card.board_id, card.id,)),
        "url": card.url,
        "short_url": card.short_url,
        "position": card.position,
        "comments": comments_json,
        "is_closed": card.is_closed,
        "creation_datetime": card.creation_datetime,
        "due_datetime": card.due_datetime,
        "spent_time": card.spent_time,
        "lead_time": card.lead_time,
        "cycle_time": card.cycle_time,
        "board": {"id": board.id, "uuid": board.uuid, "name": board.name},
        "members": [
            {"id": member.id, "trello_username": member.trello_username, "initials": member.initials}
            for member in card.members.all().order_by("initials")
        ],
        "movements": [
            {
                "id": movement.id,
                "source_list": {"id":movement.source_list.id, "name":movement.source_list.name},
                "destination_list": {"id":movement.destination_list.id, "name":movement.destination_list.name},
                "datetime": movement.datetime,
                "member": {"id": member.id, "trello_username": member.trello_username, "initials": member.initials}
            }
            for movement in card.movements.all().order_by("datetime")
        ]
    }
    return JsonResponse(card_json)