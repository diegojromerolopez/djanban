# -*- coding: utf-8 -*-

import inspect
from django import template

from djanban.apps.base import auth as djanban_auth

register = template.Library()


# Inform if user is administrator
@register.filter
def user_is_administrator(user):
    return djanban_auth.user_is_administrator(user)


# Inform if user is member
@register.filter
def user_is_member(user):
    return djanban_auth.user_is_member(user)


# Inform if user is visitor
@register.filter
def user_is_visitor(user):
    return djanban_auth.user_is_visitor(user)
