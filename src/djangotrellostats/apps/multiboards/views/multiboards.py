# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import hashlib
import time

from datetime import timedelta

import pydenticon
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards, user_is_visitor
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.forms import EditBoardForm, NewBoardForm, NewListForm, LabelForm, EditListForm
from djangotrellostats.apps.boards.models import List, Board, Label
from djangotrellostats.apps.boards.stats import avg, std_dev
from djangotrellostats.apps.fetch.fetchers.trello.boards import Initializer, BoardFetcher
from djangotrellostats.apps.multiboards.forms import MultiboardForm, DeleteMultiboardForm
from djangotrellostats.apps.multiboards.models import Multiboard
from djangotrellostats.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


@member_required
def view_list(request):
    return _view_list(request, archived=False)


@member_required
def view_archived_list(request):
    return _view_list(request, archived=True)


def _view_list(request, archived):
    member = request.user.member
    multiboards = member.created_multiboards.filter(is_archived=archived).order_by("order", "name")
    replacements = {"multiboards": multiboards, "archived": archived, "member": member}
    return render(request, "multiboards/list.html", replacements)


# New multiboard
@member_required
def new(request):
    member = request.user.member

    multiboard = Multiboard(creator=member)

    if request.method == "POST":
        form = MultiboardForm(request.POST, instance=multiboard)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("multiboards:list"))
    else:
        form = MultiboardForm(instance=multiboard)

    return render(request, "multiboards/new.html", {"form": form, "member": member})


# View a multiboard
@member_required
def view(request, multiboard_id):
    member = request.user.member
    try:
        multiboard = member.created_multiboards.get(id=multiboard_id, is_archived=False)
    except Multiboard.DoesNotExist:
        raise Http404
    replacements = {
        "multiboard": multiboard,
        "member": member,
        "boards": multiboard.boards.filter(is_archived=False).order_by("name")
    }
    return render(request, "multiboards/view.html", replacements)


# View a multiboard's task board
@member_required
def view_task_board(request, multiboard_id):
    member = request.user.member
    try:
        multiboard = member.created_multiboards.get(id=multiboard_id, is_archived=False)
    except Multiboard.DoesNotExist:
        raise Http404
    replacements = {
        "multiboard": multiboard,
        "member": member,
        "boards": multiboard.boards.filter(is_archived=False).order_by("name")
    }
    return render(request, "multiboards/view_task_board.html", replacements)


# Edition of multiboard
@member_required
def edit(request, multiboard_id):
    member = request.user.member
    try:
        multiboard = member.created_multiboards.get(id=multiboard_id)
    except Multiboard.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = MultiboardForm(request.POST, instance=multiboard)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("multiboards:list"))

    else:
        form = MultiboardForm(instance=multiboard)

    return render(request, "multiboards/edit.html", {"form": form, "multiboard": multiboard, "member": member})


# Delete a multiboard
@member_required
def delete(request, multiboard_id):
    member = request.user.member
    try:
        multiboard = member.created_multiboards.get(id=multiboard_id)
    except Multiboard.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteMultiboardForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            multiboard.delete()
            return HttpResponseRedirect(reverse("multiboards:list"))

    else:
        form = DeleteMultiboardForm()

    return render(request, "multiboards/delete.html", {"form": form, "multiboard": multiboard, "member": member})

