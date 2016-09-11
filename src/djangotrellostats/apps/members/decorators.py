# -*- coding: utf-8 -*-

from django.http import HttpResponseForbidden

from djangotrellostats.apps.base.auth import user_is_administrator


def administrator_required(the_func):
    """
    Force the view to be executed by an administrator.
    """

    def _decorated(request, *args, **kwargs):
        user = request.user
        if user_is_administrator(user):
            return the_func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return _decorated