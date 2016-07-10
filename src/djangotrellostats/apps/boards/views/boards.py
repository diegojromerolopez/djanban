# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render

from djangotrellostats.apps.boards.models import List, Fetch, DailySpentTime, Board
from djangotrellostats.apps.boards.stats import avg, std_dev
from djangotrellostats.apps.members.models import Member

# Initialize boards with data fetched from trello
def init_boards(request):
    if request.method == "POST":
        member = request.user.member
        member.init_fetch()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    raise Http404


# View boards of current user
@login_required
def view_list(request):
    member = request.user.member
    boards = member.boards.all()
    for board in boards:
        board.lists_are_configured = board.lists.filter(type="done").exists() and board.lists.filter(type="development").exists()
    replacements = {"member": member, "boards": boards}
    return render(request, "boards/list.html", replacements)


# View lists of a board
@login_required
def view_lists(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    lists = board.lists.all()
    replacements = {"member": member, "board": board, "lists": lists}
    return render(request, "boards/board_lists.html", replacements)


# Delete a board
@login_required
def delete(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.delete()
        return HttpResponseRedirect(reverse("boards:view_boards"))
    raise Http404


# Fetch cards and labels of a board
@login_required
def fetch(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.fetch()
        return HttpResponseRedirect(reverse("boards:view_boards"))
    raise Http404


# View card report
@login_required
def view_card_report(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    last_fetch = board.last_fetch()
    cards = last_fetch.cards.all()
    replacements = {
        "member": member, "fetch": last_fetch, "board": board, "cards": cards,
        "avg_lead_time": avg(cards, "lead_time"),
        "std_dev_lead_time": std_dev(cards, "lead_time"),
        "avg_cycle_time": avg(cards, "cycle_time"),
        "std_dev_cycle_time": std_dev(cards, "cycle_time"),
    }
    return render(request, "cards/list.html", replacements)


# View card report
@login_required
def view_workflow_card_report(request, board_id, workflow_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    last_fetch = board.last_fetch()
    workflow_card_reports = last_fetch.workflow_card_reports.filter(workflow_id=workflow_id)
    replacements = {
        "member": member, "fetch": last_fetch, "board": board, "workflow_card_reports": workflow_card_reports,
        "avg_lead_time": avg(workflow_card_reports, "lead_time"),
        "std_dev_lead_time": std_dev(workflow_card_reports, "lead_time"),
        "avg_cycle_time": avg(workflow_card_reports, "cycle_time"),
        "std_dev_cycle_time": std_dev(workflow_card_reports, "cycle_time"),
    }
    return render(request, "cards/workflow_card_report_list.html", replacements)


# View label report
@login_required
def view_label_report(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    last_fetch = board.last_fetch()
    labels = last_fetch.labels.all()
    replacements = {"member": member, "fetch": last_fetch, "board": board, "labels": labels}
    return render(request, "labels/list.html", replacements)


# View member report
@login_required
def view_member_report(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    last_fetch = board.last_fetch()
    member_reports = last_fetch.member_reports.all()
    replacements = {"member": member, "fetch": last_fetch, "board": board, "member_reports": member_reports}
    return render(request, "member_reports/list.html", replacements)


# Change list type. Remember a list can be "development" or "done" list
@login_required
def change_list_type(request):
    member = request.user.member
    if request.method == "POST":
        list_id = request.POST.get("list_id")
        type_ = request.POST.get("type")
        if type_ not in List.LIST_TYPES:
            raise Http404

        # If there are a done list, update it to "normal"
        if type_ == "done" and List.objects.filter(type="done").exists():
            List.objects.filter(type="done").update(type="normal")

        list_ = List.objects.get(id=list_id, board__members=member)
        list_.type = type_
        list_.save()

        return HttpResponseRedirect(reverse("boards:view_board_lists", args=(list_.board_id,)))
    raise Http404
