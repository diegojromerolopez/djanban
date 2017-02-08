# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re

import dateutil
from django.db import transaction
from django.http import JsonResponse, Http404

from djangotrellostats.apps.api.http import JsonResponseBadRequest, JsonResponseMethodNotAllowed, JsonResponseNotFound
from djangotrellostats.apps.api.serializers import serialize_card, serialize_board
from djangotrellostats.apps.api.util import get_list_or_404, get_card_or_404, get_board_or_404
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board, Card, CardComment, List
from djangotrellostats.trello_api.cards import set_name, set_description, set_is_closed, set_due_datetime, remove_due_datetime


# Point of access to several actions
@member_required
def modify_cards(request, board_id):
    # Create a new card
    if request.method == "PUT":
        return _add_card(request, board_id)

    # Move all cards in a list
    if request.method == "POST":
        return _move_all_list_cards(request, board_id)

    # Otherwise, return HTTP ERROR 405
    return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})


# Adds a new card in the board
# Used by modify_cards
def _add_card(request, board_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member

    put_params = json.loads(request.body)

    if not put_params.get("name") or not put_params.get("list") or not put_params.get("position"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    if put_params.get("position") != "top" and put_params.get("position") != "bottom":
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    try:
        list_ = get_list_or_404(request, board_id, put_params.get("list"))
    except Http404:
        return JsonResponseNotFound({"message": "List not found"})

    new_card = list_.add_card(member=member, name=put_params.get("name"), position=put_params.get("position"))

    return JsonResponse(serialize_card(new_card))


# Move all cards from a list to another
# Used by modify_cards
def _move_all_list_cards(request, board_id):
    if request.method != "POST":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        board = get_board_or_404(request, board_id)
    except Http404:
        return JsonResponseNotFound({"message": "Board not found"})

    post_params = json.loads(request.body)

    if not post_params.get("source_list") or not post_params.get("destination_list"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    # Check if the lists exists and if they are different
    try:
        source_list = board.active_lists.get(id=post_params.get("source_list"))
        destination_list = board.active_lists.get(id=post_params.get("destination_list"))
        if source_list.id == destination_list.id:
            raise AssertionError()
    except (List.DoesNotExist, AssertionError):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    # Move the cards
    source_list.move_cards(member=member, destination_list=destination_list)

    return JsonResponse(serialize_board(board))



# Return the JSON representation of a card
@member_required
def get_card(request, board_id, card_id):
    if request.method != "GET":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    card_json = serialize_card(card)
    return JsonResponse(card_json)


# Change the name or description of the card
@member_required
@transaction.atomic
def change(request, board_id, card_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})

    put_params = json.loads(request.body)

    if put_params.get("name"):
        card.name = put_params.get("name")
        card.save()
        set_name(card, member)

    elif put_params.get("description"):
        card.description = put_params.get("description")
        card.save()
        set_description(card, member)

    elif put_params.get("is_closed") is not None:
        card.is_closed = put_params.get("is_closed")
        card.save()
        set_is_closed(card, member)

    elif put_params.get("due_datetime"):
        due_datetime_str = put_params.get("due_datetime")
        card.due_datetime = dateutil.parser.parse(due_datetime_str)
        card.save()
        set_due_datetime(card, member)

    elif "due_datetime" in put_params and put_params.get("due_datetime") is None:
        card.due_datetime = None
        card.save()
        remove_due_datetime(card, member)
    else:
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    return JsonResponse(serialize_card(card))


# Change the labels of the card
@member_required
@transaction.atomic
def change_labels(request, board_id, card_id):
    if request.method != "POST":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    board = card.board

    post_params = json.loads(request.body)

    if not post_params.get("labels"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

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
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    board = card.board

    post_params = json.loads(request.body)

    if not post_params.get("members"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

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
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    post_params = json.loads(request.body)

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})

    # The new position of the card
    new_position = post_params.get("position", "top")

    # If there is no new_list param, the card is going to be moved in the same list currently is
    if post_params.get("new_list"):
        list_ = card.board.lists.get(id=post_params.get("new_list"))
        card.move(member, destination_list=list_, destination_position=new_position)
    else:
        print "X1"
        print card.list.name
        card.change_order(member, destination_position=new_position)
        print "X2"

    return JsonResponse(serialize_board(card.board))


# Creates a new comment
@member_required
@transaction.atomic
def add_new_comment(request, board_id, card_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    put_params = json.loads(request.body)

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})

    # Getting the comment content
    comment_content = put_params.get("content")

    # If the comment is empty, fail
    if not comment_content:
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

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
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})

    post_params = json.loads(request.body)
    spent_time = post_params.get("spent_time")
    estimated_time = post_params.get("estimated_time")
    date = post_params.get("date")
    description = post_params.get("description", card.name)

    if spent_time != "":
        try:
            spent_time = float(str(spent_time).replace(",", "."))
        except ValueError:
            return JsonResponseNotFound({"message": "Not found."})
    else:
        spent_time = None

    if estimated_time != "":
        try:
            estimated_time = float(str(estimated_time).replace(",", "."))
        except ValueError:
            return JsonResponseNotFound({"message": "Not found."})
    else:
        estimated_time = None

    if spent_time is None and estimated_time is None:
        return JsonResponseNotFound({"message": "Not found."})

    # Optional days ago parameter
    days_ago = None
    matches = re.match(r"^\-(?P<days_ago>\d+)$", date)
    if matches:
        days_ago = int(matches.group("days_ago"))

    card.add_spent_estimated_time(member, spent_time, estimated_time, days_ago, description)

    return JsonResponse(serialize_card(card))


# Add a new blocking card to this card
@member_required
def add_blocking_card(request, board_id, card_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    put_body = json.loads(request.body)
    if not put_body.get("blocking_card"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        blocking_card = board.cards.exclude(id=card_id).get(id=put_body.get("blocking_card"))
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        return JsonResponseNotFound({"message": "Not found."})

    card.add_blocking_card(member, blocking_card)
    return JsonResponse(serialize_card(card))


# Remove a blocking card to this card
@member_required
def remove_blocking_card(request, board_id, card_id, blocking_card_id):
    if request.method != "DELETE":
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        blocking_card = card.blocking_cards.exclude(id=card_id).get(id=blocking_card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        return JsonResponseNotFound({"message": "Not found."})

    card.remove_blocking_card(member, blocking_card)
    return JsonResponse(serialize_card(card))


# Add a new review
@member_required
@transaction.atomic
def add_new_review(request, board_id, card_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    board = card.board

    put_body = json.loads(request.body)
    if not put_body.get("members"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    reviewers = board.members.filter(id__in=put_body.get("members"))

    description = put_body.get("description", "")

    card.add_review(member, reviewers=reviewers, description=description)

    return JsonResponse(serialize_card(card))


# Delete a review
@member_required
@transaction.atomic
def delete_review(request, board_id, card_id, review_id):
    if request.method != "DELETE":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        review = card.reviews.get(id=review_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        return JsonResponseNotFound({"message": "Not found."})

    card.delete_review(member, review)
    return JsonResponse(serialize_card(card))


# Add a requirement to the card
@member_required
@transaction.atomic
def add_requirement(request, board_id, card_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    board = card.board

    put_body = json.loads(request.body)
    if not put_body.get("requirement"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    requirement = board.requirements.get(id=put_body.get("requirement"))

    # If the requirement is already in the card, we can't continue
    if card.requirements.filter(id=requirement.id).exists():
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    card.add_requirement(member, requirement)

    return JsonResponse(serialize_card(card))


# Remove a requirement of the card
@member_required
@transaction.atomic
def remove_requirement(request, board_id, card_id, requirement_id):
    if request.method != "DELETE":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        requirement = card.requirements.get(id=requirement_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        return JsonResponseNotFound({"message": "Not found."})

    card.remove_requirement(member, requirement)
    return JsonResponse(serialize_card(card))


# Delete or update a comment
@member_required
@transaction.atomic
def modify_comment(request, board_id, card_id, comment_id):
    if request.method != "DELETE" and request.method != "POST":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        card = get_card_or_404(request, board_id, card_id)
    except Http404:
        return JsonResponseNotFound({"message": "Card not found."})
    try:
        comment = card.comments.get(id=comment_id)
    except CardComment.DoesNotExist as e:
        return JsonResponseNotFound({"message": "Not found."})

    if request.method == "DELETE":
        comment = _delete_comment(member, card, comment)

    elif request.method == "POST":
        post_params = json.loads(request.body)
        new_comment_content = post_params.get("content")
        if not new_comment_content:
            return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})
        comment = _edit_comment(member, card, comment, new_comment_content)

    else:
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

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

