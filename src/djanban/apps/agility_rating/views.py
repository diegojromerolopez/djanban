# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from djanban.apps.agility_rating.forms import ProjectAgilityRatingForm, DeleteProjectAgilityRatingForm
from djanban.apps.agility_rating.models import ProjectAgilityRating
from djanban.apps.base.auth import user_is_member, get_user_boards, get_user_board_or_404
from djanban.apps.base.decorators import member_required
from djanban.apps.boards.models import Board


# View agility rating
@login_required
def view(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    board = get_user_board_or_404(request.user, board_id)

    try:
        agility_rating = board.agility_rating
    except ObjectDoesNotExist:
        agility_rating = None

    replacements = {"member": member, "board": board, "agility_rating": agility_rating}
    return render(request, "agility_rating/view.html", replacements)


# New agility rating
@member_required
def new(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member

    board = get_user_board_or_404(request.user, board_id)

    project_agility_rating = ProjectAgilityRating(board=board)

    if request.method == "POST":
        form = ProjectAgilityRatingForm(request.POST, instance=project_agility_rating)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:agility_rating:view", args=(board_id,)))
    else:
        form = ProjectAgilityRatingForm(instance=project_agility_rating)

    return render(request, "agility_rating/new.html", {"form": form, "board": board, "member": member})


# Edition of the project agility rating
@member_required
def edit(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    try:
        board = get_user_board_or_404(request.user, board_id)
        project_agility_rating = board.agility_rating
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = ProjectAgilityRatingForm(request.POST, instance=project_agility_rating)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:agility_rating:view", args=(board_id,)))

    else:
        form = ProjectAgilityRatingForm(instance=project_agility_rating)

    return render(request, "agility_rating/edit.html", {"form": form, "board": board, "member": member})


# Delete the project agility rating
@member_required
def delete(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    try:
        board = get_user_board_or_404(request.user, board_id)
        project_agility_rating = board.agility_rating
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteProjectAgilityRatingForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            project_agility_rating.delete()
            return HttpResponseRedirect(reverse("boards:agility_rating:view", args=(board_id,)))

    else:
        form = DeleteProjectAgilityRatingForm()

    replacements = {"form": form, "board": board, "member": member, "project_agility_rating": project_agility_rating}
    return render(request, "agility_rating/delete.html", replacements)
