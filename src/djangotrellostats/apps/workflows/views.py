# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.workflows.forms import NewWorkflowForm, EditWorkflowForm
from djangotrellostats.apps.workflows.models import Workflow


# View list of workflows of a board
@login_required
def view_list(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    workflows = Workflow.objects.all().order_by("name")
    # Ordered workflow lists
    for workflow in workflows:
        workflow.ordered_lists = workflow.workflow_lists.all().order_by("order")
    replacements = {"board": board, "workflows": workflows, "member": member}
    return render(request, "workflows/list.html", replacements)


# New workflow of a board
@member_required
def new(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    workflow = Workflow(name=u"New workflow", board=board)

    if request.method == "POST":
        form = NewWorkflowForm(workflow, request.POST)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:view_workflows", args=(board_id,)))

    else:
        form = NewWorkflowForm(workflow)

    return render(request, "workflows/new.html", {"form": form, "board": board, "member": member})


# Edit workflow of a board
@member_required
def edit(request, board_id, workflow_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    workflow = board.workflows.get(id=workflow_id)

    if request.method == "POST":
        form = EditWorkflowForm(workflow, request.POST, instance=workflow)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:view_workflows", args=(board_id,)))

    else:
        form = EditWorkflowForm(workflow, instance=workflow)

    return render(request, "workflows/edit.html", {"form": form, "board": board, "workflow": workflow, "member": member})


# Edit workflow of a board
@member_required
def delete(request, board_id, workflow_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    confirmed_workflow_id = request.POST.get("workflow_id")
    if confirmed_workflow_id and confirmed_workflow_id == workflow_id:
        workflow = board.workflows.get(id=confirmed_workflow_id)
        workflow.delete()
        return HttpResponseRedirect(reverse("boards:view_workflows", args=(board_id,)))

    raise Http404
