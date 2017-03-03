# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import json

from django.db import transaction
from django.http import Http404, HttpResponseBadRequest
from django.http import JsonResponse

from djangotrellostats.apps.api.http import JsonResponseMethodNotAllowed, JsonResponseNotFound
from djangotrellostats.apps.api.serializers import Serializer
from djangotrellostats.apps.api.util import get_board_or_404
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member, MemberRole


@member_required
def get_boards(request):
    if request.method != "GET":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})
    try:
        boards = get_user_boards(request.user)
    except Board.DoesNotExist:
        return JsonResponseNotFound({"message": "Not found."})

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
    if request.method != "GET":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})
    try:
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponseNotFound({"message": "Not found."})

    serializer = Serializer(board=board)
    return JsonResponse(serializer.serialize_board())


# Add a member to a board
@member_required
@transaction.atomic
def add_member(request, board_id):
    if request.method != "PUT":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    put_body = json.loads(request.body)

    if not put_body.get("member"):
        return HttpResponseBadRequest()

    member_id = put_body.get("member")

    try:
        board = get_board_or_404(request, board_id)
    except Http404:
        return JsonResponseNotFound({"message": "Board not found"})

    serializer = Serializer(board=board)

    if board.members.filter(id=member_id).exists():
        return JsonResponse(serializer.serialize_member(board.members.get(id=member_id)))

    member_type = put_body.get("member_type")
    if not member_type or not member_type in ("admin", "normal", "guest"):
        return JsonResponseNotFound({"message": "Member type not found"})

    try:
        new_member = Member.objects.get(id=member_id)
        board.add_member(member=member, member_to_add=new_member)
        member_role, member_role_created = MemberRole.objects.get_or_create(board=board, type=member_type)
        member_role.members.add(new_member)
    except Member.DoesNotExist:
        return JsonResponseNotFound({"message": "Not found."})

    return JsonResponse(serializer.serialize_member(new_member))


# Delete member from board
@member_required
@transaction.atomic
def remove_member(request, board_id, member_id):
    if request.method != "DELETE":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member
    try:
        board = get_board_or_404(request, board_id)
    except Http404:
        return JsonResponseNotFound({"message": "Board not found"})

    try:
        member_to_remove = board.members.get(id=member_id)
        board.remove_member(member=member, member_to_remove=member_to_remove)
    except Member.DoesNotExist:
        return JsonResponseNotFound({"message": "Member nor found."})

    serializer = Serializer(board=board)
    return JsonResponse(serializer.serialize_member(member_to_remove))
