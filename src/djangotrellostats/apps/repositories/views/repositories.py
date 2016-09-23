# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DeleteView

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.repositories.forms import GitLabRepositoryForm, get_form_class, DeleteRepositoryForm, \
    GitHubPublicRepositoryForm
from djangotrellostats.apps.repositories.models import Repository, GitLabRepository, GitHubPublicRepository


# List of repositories
@member_required
def view_list(request, board_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
    repositories = board.repositories.all().order_by("name")
    replacements = {
        "member": member,
        "board": board,
        "repositories": repositories
    }
    return render(request, "repositories/list.html", replacements)


# View a repository
@member_required
def view(request, board_id, repository_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
    except (Board.DoesNotExist, Repository.DoesNotExist):
        raise Http404

    replacements = {
        "member": member,
        "board": board,
        "repository": repository
    }
    return render(request, "repositories/view.html", replacements)


# New repository
@member_required
def new(request, board_id, type="gitlab"):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    if type == "gitlab":
        repository_class = GitLabRepository
        form_class = GitLabRepositoryForm
    elif type == "github":
        repository_class = GitHubPublicRepository
        form_class = GitHubPublicRepositoryForm
    else:
        raise Http404

    repository = repository_class(board=board)

    if request.method == "POST":
        form = form_class(request.POST, instance=repository)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:repositories:view_repositories", args=(board_id,)))
    else:
        form = form_class(instance=repository)

    return render(request, "repositories/new.html", {"form": form, "board": board, "member": member})


# Edition of a repository
@member_required
def edit(request, board_id, repository_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
    except ObjectDoesNotExist:
        raise Http404

    derived_object = repository.derived_object
    form_class = get_form_class(derived_object)

    if request.method == "POST":
        form = form_class(request.POST, instance=derived_object)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:repositories:view_repositories", args=(board_id,)))

    else:
        form = form_class(instance=derived_object)

    replacements = {"form": form, "board": board, "member": member, "repository": repository}
    return render(request, "repositories/edit.html", replacements)


# Checkout of a repository
@member_required
def checkout(request, board_id, repository_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
    except ObjectDoesNotExist:
        raise Http404

    repository.checkout()
    return HttpResponseRedirect(reverse("boards:repositories:view_repository", args=(board_id, repository.id)))


# Delete a repository
@member_required
def delete(request, board_id, repository_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteRepositoryForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            repository.delete()
            return HttpResponseRedirect(reverse("boards:repositories:view_repositories", args=(board_id,)))

    else:
        form = DeleteRepositoryForm()

    replacements = {"form": form, "board": board, "member": member, "repository": repository}
    return render(request, "repositories/delete.html", replacements)
