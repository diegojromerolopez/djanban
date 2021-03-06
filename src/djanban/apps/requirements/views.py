# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from djanban.apps.base.auth import user_is_member, get_user_boards, get_user_board_or_404
from djanban.apps.base.decorators import member_required
from djanban.apps.boards.models import Board
from djanban.apps.requirements.forms import NewRequirementForm, EditRequirementForm, DeleteRequirementForm
from djanban.apps.requirements.models import Requirement


# List of requirements
@login_required
def view_list(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member

    board = get_user_board_or_404(request.user, board_id)
    requirements = board.requirements.all().order_by("value")
    replacements = {
        "member": member,
        "board": board,
        "requirements": requirements
    }
    return render(request, "requirements/list.html", replacements)


# View a requirement
@login_required
def view(request, board_id, requirement_code):

    member = None
    if user_is_member(request.user):
        member = request.user.member

    board = get_user_board_or_404(request.user, board_id)

    requirement = get_object_or_404(Requirement, code=requirement_code, board=board)
    replacements = {
        "member": member,
        "board": board,
        "requirement": requirement
    }
    return render(request, "requirements/view.html", replacements)


# New requirement
@member_required
def new(request, board_id):
    member = request.user.member
    board = get_user_board_or_404(request.user, board_id)

    requirement = Requirement(board=board)

    if request.method == "POST":
        form = NewRequirementForm(request.POST, instance=requirement)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:requirements:view_requirements", args=(board_id,)))
    else:
        form = NewRequirementForm(instance=requirement)

    return render(request, "requirements/new.html", {"form": form, "board": board, "member": member})


# Edition of requirement
@member_required
def edit(request, board_id, requirement_code):
    member = request.user.member
    board = get_user_board_or_404(request.user, board_id)

    try:
        requirement = board.requirements.get(code=requirement_code)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EditRequirementForm(request.POST, instance=requirement)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:requirements:view_requirements", args=(board_id,)))

    else:
        form = EditRequirementForm(instance=requirement)

    return render(request, "requirements/edit.html", {"form": form, "board": board, "member": member})


# Delete a requirement
@member_required
def delete(request, board_id, requirement_code):
    member = request.user.member
    board = get_user_board_or_404(request.user, board_id)

    try:
        requirement = board.requirements.get(code=requirement_code)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteRequirementForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            requirement.delete()
            return HttpResponseRedirect(reverse("boards:requirements:view_requirements", args=(board_id,)))

    else:
        form = DeleteRequirementForm()

    return render(request, "requirements/delete.html", {"form": form, "board": board, "member": member, "requirement": requirement})


