# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import json

from django.db import transaction
from django.http import Http404, HttpResponseBadRequest
from django.http import JsonResponse
from django.urls import reverse

from djangotrellostats.apps.api.http import HttpResponseMethodNotAllowed
from djangotrellostats.apps.api.serializers import serialize_list, serialize_member, serialize_requirement, \
    serialize_board
from djangotrellostats.apps.api.util import get_board_or_404
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member


@member_required
def get_boards(request):
    if request.method != "GET":
        return HttpResponseMethodNotAllowed()
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
    if request.method != "GET":
        return HttpResponseMethodNotAllowed()
    try:
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    return JsonResponse(serialize_board(board))


# Add a member to a board
@member_required
@transaction.atomic
def add_member(request, board_id):
    if request.method != "PUT":
        return HttpResponseMethodNotAllowed()

    member = request.user.member
    put_body = json.loads(request.body)

    if not put_body.get("member"):
        return HttpResponseBadRequest()

    member_id = put_body.get("member")

    board = get_board_or_404(request, board_id)

    if board.members.filter(id=member_id).exists():
        return JsonResponse(serialize_member(board.members.get(id=member_id)))

    try:
        new_member = Member.objects.get(id=member_id)
        board.add_member(member=member, member_to_add=new_member)
    except Member.DoesNotExist:
        raise Http404

    return JsonResponse(serialize_member(new_member))


# Delete member from board
@member_required
@transaction.atomic
def remove_member(request, board_id, member_id):
    if request.method != "DELETE":
        return HttpResponseMethodNotAllowed()

    member = request.user.member
    board = get_board_or_404(request, board_id)
    try:
        member_to_remove = board.members.get(id=member_id)
        board.remove_member(member=member, member_to_remove=member_to_remove)
    except Member.DoesNotExist:
        raise Http404
    return JsonResponse(serialize_member(member_to_remove))
