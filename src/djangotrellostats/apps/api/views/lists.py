# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import json
import re

from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse

from djangotrellostats.apps.api.http import HttpResponseMethodNotAllowed
from djangotrellostats.apps.api.serializers import serialize_list
from djangotrellostats.apps.api.util import get_list_or_404
from djangotrellostats.apps.base.decorators import member_required


# Move a list
@member_required
@transaction.atomic
def move_list(request, board_id, list_id):

    if request.method != "POST":
        return HttpResponseMethodNotAllowed()

    member = request.user.member

    list_ = get_list_or_404(request, board_id, list_id)
    board = list_.board

    post_params = json.loads(request.body)

    if not post_params.get("position"):
        return HttpResponseBadRequest()

    position = post_params.get("position")
    if position != "top" and position != "bottom" and not re.match(r"^\d+", position):
        return HttpResponseBadRequest()

    list_.move(member, position)
    return JsonResponse(serialize_list(list_))
