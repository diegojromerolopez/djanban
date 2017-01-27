# -*- coding: utf-8 -*-
import json

from django.http import HttpResponseBadRequest
from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Board, Card, CardComment


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
            "last_edition_datetime": comment.last_edition_datetime
            ,
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


# Creates a new comment
def add_new_comment(request, board_id, card_id):
    if request.method != "PUT":
        raise Http404

    put_params = json.loads(request.body)

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        raise Http404

    # Getting the comment content
    comment_content = put_params.get("content")

    # If the comment is empty, fail
    if not comment_content:
        return HttpResponseBadRequest()

    # Otherwise, add the comment
    new_comment = card.add_comment(member, comment_content)
    author = new_comment.author

    return JsonResponse({
            "id": new_comment.id,
            "uuid": new_comment.uuid,
            "content": new_comment.content,
            "creation_datetime": new_comment.creation_datetime,
            "author": {"id": author.id, "trello_username": author.trello_username, "initials": author.initials}
    })


# Delete or update a comment
def modify_comment(request, board_id, card_id, comment_id):
    if request.method != "DELETE" and request.method != "POST":
        print "fasdfas"
        return HttpResponseBadRequest()

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        comment = card.comments.get(id=comment_id)
    except (Board.DoesNotExist, Card.DoesNotExist, CardComment.DoesNotExist) as e:
        print e
        raise Http404

    if request.method == "DELETE":
        comment = _delete_comment(member, card, comment)

    elif request.method == "POST":
        post_params = json.loads(request.body)
        new_comment_content = post_params.get("content")
        if not new_comment_content:
            return HttpResponseBadRequest()
        comment = _edit_comment(member, card, comment, new_comment_content)

    else:
        return HttpResponseBadRequest()

    author = comment.author

    return JsonResponse({
        "id": comment.id,
        "uuid": comment.uuid,
        "content": comment.content,
        "creation_datetime": comment.creation_datetime,
        "author": {"id": author.id, "trello_username": author.trello_username, "initials": author.initials}
    })


# Edit comment
def _edit_comment(member, card, comment_to_edit, new_comment_content):
    edited_comment = card.edit_comment(member, comment_to_edit, new_comment_content)
    return edited_comment


# Delete a comment
def _delete_comment(member, card, comment_to_delete):
    # Delete the comment
    card.delete_comment(member, comment_to_delete)
    return comment_to_delete

