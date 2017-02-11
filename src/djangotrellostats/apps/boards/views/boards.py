# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import time

from datetime import timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards, user_is_visitor
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.forms import EditBoardForm, NewBoardForm, NewListForm, LabelForm
from djangotrellostats.apps.boards.models import List, Board, Label
from djangotrellostats.apps.boards.stats import avg, std_dev
from djangotrellostats.apps.fetch.fetchers.trello.boards import Initializer, BoardFetcher
from djangotrellostats.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


# Initialize boards with data fetched from trello
@member_required
def init_boards(request):
    if request.method == "POST":
        member = request.user.member
        initializer = Initializer(member)
        initializer.init()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    raise Http404


@member_required
def new(request):
    member = request.user.member

    board = Board(creator=member)

    if request.method == "POST":
        form = NewBoardForm(request.POST, instance=board)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:view_boards"))
    else:
        form = NewBoardForm(instance=board)

    return render(request, "boards/new.html", {"form": form, "board": board, "member": member})


# Create boards that are present in Trello but not in this platform
@member_required
def sync(request):
    member = request.user.member

    # Only members with credentials can sync their boards
    if not member.has_trello_credentials:
        return HttpResponseRedirect(reverse("boards:view_boards"))

    if request.method == "POST":
        initializer = Initializer(member)
        initializer.init()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    return render(request, "boards/sync.html", {"member": member})


@member_required
def create_default_labels(request, board_id):
    member = request.user.member

    # Only members with credentials can sync their boards
    if member.has_trello_profile:
        return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))

    if request.method != "POST":
        return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))

    board = get_user_boards(request.user).get(id=board_id)
    if board.labels.all().exists():
        return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))

    Label.create_default_labels(board)

    return HttpResponseRedirect(reverse("boards:view_label_report", args=(board_id,)))


@member_required
def edit_label(request, board_id, label_id):
    member = request.user.member
    board = member.boards.get(id=board_id)

    try:
        label = board.labels.get(id=label_id)
    except Label.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = LabelForm(request.POST, instance=label)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("boards:view_label_report", args=(board_id,)))

    else:
        form = LabelForm(instance=label)

    replacements = {"board": board, "member": member, "form": form, "label": label}
    return render(request, "boards/labels/edit.html", replacements)


# View boards of current user
@login_required
def view_list(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    boards = get_user_boards(request.user).order_by("name")
    archived_boards = get_user_boards(request.user, is_archived=True).order_by("name")
    replacements = {"member": member, "boards": boards, "archived_boards": archived_boards}
    return render(request, "boards/list.html", replacements)


# View archived boards
@member_required
def view_archived_boards(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    boards = get_user_boards(request.user, is_archived=True).order_by("name")
    replacements = {"member": member, "boards": boards}
    return render(request, "boards/archived_list.html", replacements)


# View a board stats panorama
@login_required
def view_board_panorama(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    replacements = {"member": member}
    return render(request, "boards/panorama.html", replacements)


# View board gantt chart
@login_required
def view_gantt_chart(request, board_id):
    try:
        board = get_user_boards(request.user).get(id=board_id)
        member = None
        visitor = None
        if user_is_member(request.user):
            member = request.user.member
        elif user_is_visitor(request.user, board):
            visitor = request.user
    except Board.DoesNotExist:
        raise Http404

    board_cards = board.cards.filter(list__type__in=List.STARTED_CARD_LIST_TYPES)

    cards = []
    for board_card in board_cards:

        # Task start
        start_date = board_card.start_datetime
        if start_date is None:
            start_date = board_card.creation_datetime

        # Task end
        if board_card.due_datetime is not None:
            end_date = board_card.due_datetime
        elif board_card.list.type == "done":
            end_date = board_card.end_datetime
        else:
            end_date = start_date + timedelta(days=1)

        # Color of task
        task_color = "black"
        labels = board_card.labels.all()
        if labels.exists():
            main_label = labels[0]
            task_color = main_label.color

        # Percentage of completion of the task
        if board_card.list.type == "development":
            completion_percentage = 0
        elif board_card.list.type == "after_development_in_review":
            completion_percentage = 75
        elif board_card.list.type == "after_development_waiting_release":
            completion_percentage = 85
        else:
            completion_percentage = 100

        # Parent Task
        blocking_cards = board_card.blocking_cards.all().order_by("creation_datetime")
        parent_card = 0
        if blocking_cards.exists():
            parent_card = blocking_cards[0].id

        # Dependant tasks
        blocked_cards = board_card.blocked_cards.all()
        dependant_cards = ""
        if blocked_cards.exists():
            for blocked_card in blocked_cards:
                dependant_cards += ",".format(blocked_card.id)
            dependant_cards = dependant_cards[:-1]

        members = board_card.members.all()[:1]
        for member in members:
            card = {
                "pID": board_card.id,
                "pName": board_card.name,
                "pStart": start_date.strftime("%Y-%m-%d"),
                "pEnd": end_date.strftime("%Y-%m-%d"),
                "pClass": "gtask{0}".format(task_color),
                "pLink": reverse("boards:view_card", args=(board_id, board_card.id)),
                "pMile": 0,
                "pRes": member.external_username,
                "pComp": completion_percentage,
                "pGroup": 1 if blocked_cards.exists() else 0,
                "pParent": parent_card,
                "pOpen": 0,
                "pDepend": dependant_cards,
                "pCaption": board_card.name,
                "pNotes": board_card.description
            }
            cards.append(card)

    replacements = {
        "board": board,
        "cards": cards,
        "member": member,
        "visitor": visitor,
    }
    return render(request, "boards/gantt_chart.html", replacements)


# Dynamic task board view
@member_required
def view_dashboard(request, board_id, path=""):
    try:
        board = get_user_boards(request.user).get(id=board_id)
        member = None
        if user_is_member(request.user):
            member = request.user.member
    except Board.DoesNotExist:
        raise Http404

    replacements = {
        "member": member,
        "board": board,
        "ANGULAR_URL": settings.ANGULAR_URL,
        "DOMAIN": settings.DOMAIN,
        "PORT": settings.PORT
    }
    return render(request, "boards/view_dashboard.html", replacements)


# View board
@login_required
def view(request, board_id):
    try:
        board = get_user_boards(request.user).get(id=board_id)
        member = None
        visitor = None
        if user_is_member(request.user):
            member = request.user.member
        elif user_is_visitor(request.user, board):
            visitor = request.user

    except Board.DoesNotExist:
        raise Http404

    week_of_year = get_week_of_year()
    lists = board.lists.exclude(Q(type="ignored") | Q(type="closed")).order_by("position")

    # Next cards by due date
    next_due_date_cards = board.cards\
        .filter(due_datetime__isnull=False)\
        .exclude(
            Q(list__type="ignored") | Q(list__type="closed")
        ).order_by("-due_datetime")

    # Requirements
    requirements = board.requirements.all().order_by("-value")
    requirement = None
    if requirements.exists():
        requirement = requirements[0]

    # Replacements in the template
    replacements = {
        "url_prefix": "http://{0}".format(settings.DOMAIN),
        "board": board,
        "next_due_date_cards": next_due_date_cards,
        "lists": lists,
        "requirement": requirement,
        "requirements": requirements,
        "week_of_year": week_of_year,
        "member": member,
        "visitor": visitor,
        "weeks_of_year": get_weeks_of_year_since_one_year_ago()
    }
    return render(request, "boards/view.html", replacements)


# Public view for other stakeholders that do not have access to the board
def public_view(request, board_public_access_code):
    board = get_object_or_404(Board, enable_public_access=True, public_access_code=board_public_access_code)
    week_of_year = get_week_of_year()
    lists = board.lists.exclude(type="ignored").order_by("position")
    # Requirements
    requirements = board.requirements.all().order_by("-value")
    requirement = None
    if requirements.exists():
        requirement = requirements[0]
    replacements = {
        "requirement": requirement,
        "requirements": requirements,
        "board": board,
        "lists": lists,
        "week_of_year": week_of_year,
        "weeks_of_year": get_weeks_of_year_since_one_year_ago()
    }
    return render(request, "boards/public_view.html", replacements)


# Edit board
@member_required
def edit(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)

    if request.method == "POST":
        form = EditBoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))

    else:
        form = EditBoardForm(instance=board)

    replacements = {"board": board, "member": member, "form": form}
    return render(request, "boards/edit.html", replacements)


# View lists of a board
@member_required
def view_lists(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    lists = board.lists.all().order_by("position")
    replacements = {"member": member, "board": board, "lists": lists, "list_types": List.LIST_TYPE_CHOICES}
    return render(request, "boards/lists/list.html", replacements)


# Create a new list
@member_required
def new_list(request, board_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    list_ = List(board=board)

    # Setting maximum position of this new list (this list will be the last)
    lists = board.lists.all().order_by("-position")
    if lists.exists():
        list_.position = lists[0].position + 10

    if request.method == "POST":
        form = NewListForm(request.POST, instance=list_)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:view_lists", args=(board_id,)))
    else:
        form = NewListForm(instance=list_)

    return render(request, "boards/lists/new.html", {"form": form, "board": board, "member": member})


# Archive a board
@member_required
def archive(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id, is_archived=False)

    # Show delete form
    if request.method == "GET":
        replacements = {"member": member, "board": board}
        return render(request, "boards/archive.html", replacements)

    # Delete action by post
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.archive()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    raise Http404


# Unarchive a board
@member_required
def unarchive(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id, is_archived=True)

    # Show un-archive form
    if request.method == "GET":
        replacements = {"member": member, "board": board}
        return render(request, "boards/unarchive.html", replacements)

    # Un-archive action by post
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.unarchive()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    raise Http404


# Delete a board
@member_required
def delete(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id, is_archived=True)

    # Show delete form
    if request.method == "GET":
        replacements = {"member": member, "board": board}
        return render(request, "boards/delete.html", replacements)

    # Delete action by post
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.delete()
        return HttpResponseRedirect(reverse("boards:view_boards"))

    raise Http404


# Fetch cards and labels of a board
@member_required
def fetch(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)

    replacements = {"member": member, "board": board}

    # Show fetch form
    if request.method == "GET":
        return render(request, "boards/fetch.html", replacements)

    # Confirm fetch form
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        try:
            start_time = time.time()
            board_fetcher = BoardFetcher(board)
            board_fetcher.fetch(debug=True)
            end_time = time.time()
            print("Elapsed time {0} s".format(end_time-start_time))
            replacements["done"] = True
            return render(request, "boards/fetch.html", replacements)
        except UnicodeDecodeError as e:
            replacements["exception_message"] = e
            return render(request, "boards/fetch_error.html", replacements)

    raise Http404


# View workflow card report
@login_required
def view_workflow_card_report(request, board_id, workflow_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    workflow = board.workflows.get(id=workflow_id)
    workflow_card_reports = board.workflow_card_reports.filter(workflow_id=workflow_id)

    replacements = {
        "workflow": workflow,
        "member": member, "board": board, "workflow_card_reports": workflow_card_reports,
        "avg_lead_time": avg(workflow_card_reports, "lead_time"),
        "std_dev_lead_time": std_dev(workflow_card_reports, "lead_time"),
        "avg_cycle_time": avg(workflow_card_reports, "cycle_time"),
        "std_dev_cycle_time": std_dev(workflow_card_reports, "cycle_time"),
    }
    return render(request, "boards/cards/workflow_card_report_list.html", replacements)


# View label report
@login_required
def view_label_report(request, board_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
    labels = board.labels.exclude(name="")
    replacements = {"member": member, "board": board, "labels": labels}
    return render(request, "boards/labels/list.html", replacements)


# View member report
@login_required
def view_member_report(request, board_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    member_reports = board.member_reports.all()
    week_of_year = get_week_of_year()

    replacements = {
        "member": member,
        "board": board,
        "member_reports": member_reports,
        "week_of_year": week_of_year,
        "weeks_of_year": get_weeks_of_year_since_one_year_ago()
    }
    return render(request, "boards/member_reports/list.html", replacements)


# Change list type. Remember a list can be "development" or "done" list
@member_required
def change_list_type(request):
    member = request.user.member
    if request.method == "POST":
        list_id = request.POST.get("list_id")
        type_ = request.POST.get("type")
        if type_ not in List.LIST_TYPES:
            raise Http404

        list_ = List.objects.get(id=list_id, board__members=member)
        list_.type = type_
        list_.save()

        return HttpResponseRedirect(reverse("boards:view_lists", args=(list_.board_id,)))
    raise Http404
