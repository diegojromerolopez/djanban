# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import json
import re

from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse, Http404

from djangotrellostats.apps.api.http import HttpResponseMethodNotAllowed, JsonResponseBadRequest, \
    JsonResponseMethodNotAllowed, JsonResponseNotFound
from djangotrellostats.apps.api.serializers import serialize_list
from djangotrellostats.apps.api.util import get_list_or_404
from djangotrellostats.apps.base.decorators import member_required


# Move a list
@member_required
@transaction.atomic
def move_list(request, board_id, list_id):

    if request.method != "POST":
        return JsonResponseMethodNotAllowed({"message": "HTTP method not allowed."})

    member = request.user.member

    try:
        list_ = get_list_or_404(request, board_id, list_id)
    except Http404:
        return JsonResponseNotFound({"message": "List not found"})

    post_params = json.loads(request.body)

    if not post_params.get("position"):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    position = post_params.get("position")
    if position != "top" and position != "bottom" and not re.match(r"^\d+", position):
        return JsonResponseBadRequest({"message": "Bad request: some parameters are missing."})

    list_.move(member, position)
    return JsonResponse(serialize_list(list_))
