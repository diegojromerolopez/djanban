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


@member_required
def add_card(request, board_id):
    if request.method != "PUT":
        raise Http404

    member = request.user.member

    put_params = json.loads(request.body)

    if not put_params.get("name") or not put_params.get("list") or not put_params.get("position"):
        return HttpResponseBadRequest()

    if put_params.get("position") != "top" and put_params.get("position") != "bottom":
        return HttpResponseBadRequest()

    list_ = _get_list_or_404(request, board_id, put_params.get("list"))

    new_card = list_.add_card(member=member, name=put_params.get("name"), position=put_params.get("position"))

    return JsonResponse(serialize_card(new_card))


@member_required
def get_card(request, board_id, card_id):
    card = _get_card_or_404(request, board_id, card_id)
    card_json = serialize_card(card)
    return JsonResponse(card_json)


@member_required
@transaction.atomic
def change(request, board_id, card_id):
    if request.method != "PUT":
        raise Http404

    member = request.user.member
    card = _get_card_or_404(request, board_id, card_id)

    put_params = json.loads(request.body)

    if put_params.get("name"):
        card.name = put_params.get("name")
        card.save()
        set_name(card, member)

    elif put_params.get("description"):
        card.description = put_params.get("description")
        card.save()
        set_description(card, member)

    else:
        return HttpResponseBadRequest()

    return JsonResponse(serialize_card(card))


@member_required
@transaction.atomic
def change_labels(request, board_id, card_id):
    if request.method != "POST":
        raise Http404

    card = _get_card_or_404(request, board_id, card_id)
    board = card.board

    post_params = json.loads(request.body)

    if not post_params.get("labels"):
        return HttpResponseBadRequest()

    label_ids = post_params.get("labels")
    card.labels.clear()
    for label_id in label_ids:
        if board.labels.filter(id=label_id).exists():
            label = board.labels.get(id=label_id)
            card.labels.add(label)

    return JsonResponse(serialize_card(card))


@member_required
@transaction.atomic
def change_members(request, board_id, card_id):
    if request.method != "POST":
        raise Http404

    card = _get_card_or_404(request, board_id, card_id)
    board = card.board

    post_params = json.loads(request.body)

    if not post_params.get("members"):
        return HttpResponseBadRequest()

    member_ids = post_params.get("members")
    card.members.clear()
    for member_id in member_ids:
        if board.members.filter(id=member_id).exists():
            member = board.members.get(id=member_id)
            card.members.add(member)

    return JsonResponse(serialize_card(card))


# Change list
@member_required
@transaction.atomic
def move_to_list(request, board_id, card_id):
    if request.method != "POST":
        raise Http404

    post_params = json.loads(request.body)

    member = request.user.member
    card = _get_card_or_404(request, board_id, card_id)

    if not post_params.get("new_list"):
        return HttpResponseBadRequest()

    list_ = card.board.lists.get(id=post_params.get("new_list"))

    new_position = post_params.get("position", "top")

    card.move(member, destination_list=list_, destination_position=new_position)

    return JsonResponse(serialize_card(card))


# Creates a new comment
@member_required
@transaction.atomic
def add_new_comment(request, board_id, card_id):
    if request.method != "PUT":
        raise Http404

    put_params = json.loads(request.body)

    member = request.user.member
    card = _get_card_or_404(request, board_id, card_id)

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


# Add S/E time to card
@member_required
@transaction.atomic
def add_se_time(request, board_id, card_id):
    if request.method != "POST":
        return HttpResponseBadRequest()

    member = request.user.member
    card = _get_card_or_404(request, board_id, card_id)

    post_params = json.loads(request.body)
    spent_time = post_params.get("spent_time")
    estimated_time = post_params.get("estimated_time")
    date = post_params.get("date")
    description = post_params.get("description", card.name)

    if spent_time != "":
        try:
            spent_time = float(str(spent_time).replace(",", "."))
        except ValueError:
            raise Http404
    else:
        spent_time = None

    if estimated_time != "":
        try:
            estimated_time = float(str(estimated_time).replace(",", "."))
        except ValueError:
            raise Http404
    else:
        estimated_time = None

    if spent_time is None and estimated_time is None:
        raise Http404

    # Optional days ago parameter
    days_ago = None
    matches = re.match(r"^\-(?P<days_ago>\d+)$", date)
    if matches:
        days_ago = int(matches.group("days_ago"))

    card.add_spent_estimated_time(member, spent_time, estimated_time, days_ago, description)

    return JsonResponse(serialize_card(card))


# Delete or update a comment
@member_required
@transaction.atomic
def modify_comment(request, board_id, card_id, comment_id):
    if request.method != "DELETE" and request.method != "POST":
        return HttpResponseBadRequest()

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        comment = card.comments.get(id=comment_id)
    except (Board.DoesNotExist, Card.DoesNotExist, CardComment.DoesNotExist) as e:
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
@member_required
def _edit_comment(member, card, comment_to_edit, new_comment_content):
    edited_comment = card.edit_comment(member, comment_to_edit, new_comment_content)
    return edited_comment


# Delete a comment
@member_required
def _delete_comment(member, card, comment_to_delete):
    # Delete the comment
    card.delete_comment(member, comment_to_delete)
    return comment_to_delete


# Returns the card with id card_id
# if this is not a user's card or doesn't exist, raise 404.
def _get_card_or_404(request, board_id, card_id):
    try:
        board = _get_board_or_404(request, board_id)
        return board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist):
        raise Http404


# Returns the list with id equals to list_id
# if the list does not belong to the board with board_id or it does not exist (or is closed)
# raises a 404 error.
def _get_list_or_404(request, board_id, list_id):
    try:
        board = _get_board_or_404(request, board_id)
        return board.active_lists.get(id=list_id)
    except (Board.DoesNotExist, List.DoesNotExist):
        raise Http404


# Returns the board with id board_id
# if this is not a user's board or it doesn't exist, raise 404.
def _get_board_or_404(request, board_id):
    try:
        return get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
