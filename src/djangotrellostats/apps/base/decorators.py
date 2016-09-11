# -*- coding: utf-8 -*-

from django.http import Http404
from django.http import HttpResponseForbidden
from djangotrellostats.apps.base.auth import user_is_member


# Required this user to be a member
def member_required(a_view):
    def _wrapped_view(request, *args, **kwargs) :
        if user_is_member(request.user):
            return a_view(request, *args, **kwargs)
        return HttpResponseForbidden()
    return _wrapped_view
