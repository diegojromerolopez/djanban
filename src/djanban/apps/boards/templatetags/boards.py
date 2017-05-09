# -*- coding: utf-8 -*-

import inspect
from django import template
from crequest.middleware import CrequestMiddleware

from djanban.apps.base.auth import get_user_boards
from djanban.apps.boards.models import CardComment, List

register = template.Library()


# Return the last comments of the boards of the current user
@register.assignment_tag
def last_comments(number_of_comments=10):
    current_request = CrequestMiddleware.get_request()
    boards = get_user_boards(current_request.user)
    last_comments_ = CardComment.objects.filter(card__board__in=boards, card__is_closed=False).order_by("-creation_datetime")
    return last_comments_[:number_of_comments]


# Custom filter to get the list type name
# Return the name of the list type passed as parameter
def get_list_type_name(list_type):
    return dict(List.LIST_TYPE_CHOICES)[list_type]