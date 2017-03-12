# -*- coding: utf-8 -*-

import inspect
from django import template
from crequest.middleware import CrequestMiddleware

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import CardComment


register = template.Library()


# Return the last comments of the boards of the current user
@register.assignment_tag
def last_comments(number_of_comments=10):
    current_request = CrequestMiddleware.get_request()
    boards = get_user_boards(current_request.user)
    last_comments_ = CardComment.objects.filter(card__board__in=boards, card__is_closed=False).order_by("-creation_datetime")
    return last_comments_[:number_of_comments]
