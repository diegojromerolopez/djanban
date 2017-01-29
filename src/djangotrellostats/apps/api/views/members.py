# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import json

from django.db import transaction
from django.http import Http404, HttpResponseBadRequest
from django.http import JsonResponse
from django.urls import reverse

from djangotrellostats.apps.api.serializers import serialize_list, serialize_member
from djangotrellostats.apps.api.util import get_board_or_404
from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member


@member_required
def get_members(request):
    members = Member.objects.all()

    response_json = []
    for member in members:
        response_json.append(serialize_member(member))

    return JsonResponse(response_json, safe=False)