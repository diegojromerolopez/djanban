# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DeleteView

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.repositories.forms import GitLabRepositoryForm, get_form_class, DeleteRepositoryForm, \
    CommitForm, DeleteCommitForm
from djangotrellostats.apps.repositories.models import Repository, GitLabRepository, Commit


@login_required
def add(request, board_id, repository_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
    except ObjectDoesNotExist:
        raise Http404

    commit = Commit(repository=repository)

    if request.method == "POST":
        form = CommitForm(request.POST, instance=commit)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:repositories:view_repository", args=(board_id, repository_id)))

    else:
        form = CommitForm(instance=commit)

    replacements = {"form": form, "board": board, "member": member, "repository": repository}
    return render(request, "repositories/add_commit.html", replacements)


# Delete a commit
@login_required
def delete(request, board_id, repository_id, commit_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        repository = board.repositories.get(id=repository_id)
        commit = repository.commits.get(id=commit_id)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteCommitForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            commit.delete()
            return HttpResponseRedirect(reverse("boards:requirements:view_repository", args=(board_id, repository_id)))

    else:
        form = DeleteCommitForm()

    replacements = {"form": form, "board": board, "member": member, "repository": repository, "commit": commit}
    return render(request, "repositories/delete_commit.html", replacements)