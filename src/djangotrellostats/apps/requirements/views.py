from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import DeleteView

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.requirements.forms import NewRequirementForm, EditRequirementForm, DeleteRequirementForm
from djangotrellostats.apps.requirements.models import Requirement


# List of requirements
@login_required
def view_list(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    requirements = board.requirements.all()
    replacements = {
        "board": board,
        "requirements": requirements
    }
    return render(request, "requirements/list.html", replacements)


# View a requirement
@login_required
def view(request, board_id, requirement_code):
    board = get_object_or_404(Board, id=board_id)
    requirement = get_object_or_404(Requirement, code=requirement_code, board=board)
    replacements = {
        "board": board,
        "requirement": requirement,
        "done_cards": requirement.cards.filter(list__type="done"),
        "pending_cards": requirement.cards.exclude(list__type="done")
    }
    return render(request, "requirements/view.html", replacements)


@login_required
def new(request, board_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    requirement = Requirement(board=board)

    if request.method == "POST":
        form = NewRequirementForm(request.POST, instance=requirement)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:requirements:view_requirements", args=(board_id,)))
    else:
        form = NewRequirementForm(instance=requirement)

    return render(request, "requirements/new.html", {"form": form, "board": board, "member": member})


@login_required
def edit(request, board_id, requirement_code):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
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


@login_required
def delete(request, board_id, requirement_code):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
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


