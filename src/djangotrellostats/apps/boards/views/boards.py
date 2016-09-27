# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.template.context import Context
from django.conf import settings

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards, user_is_visitor
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.forms import EditBoardForm
from djangotrellostats.apps.boards.models import List, Board, Card
from djangotrellostats.apps.boards.stats import avg, std_dev

from djangotrellostats.apps.fetch.fetchers.trello import BoardFetcher, Initializer
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


# View boards of current user
@login_required
def view_list(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    boards = get_user_boards(request.user).order_by("name")
    replacements = {"member": member, "boards": boards}
    return render(request, "boards/list.html", replacements)


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
    lists = board.lists.exclude(type="ignored").order_by("position")

    # Requirements
    requirements = board.requirements.all().order_by("-value")
    requirement = None
    if requirements.exists():
        requirement = requirements[0]

    # Replacements in the template
    replacements = {
        "url_prefix": "http://{0}".format(settings.DOMAIN),
        "board": board,
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
    lists = board.lists.all()
    list_types = {list_type_par[0]: list_type_par[1] for list_type_par in List.LIST_TYPE_CHOICES}
    replacements = {"member": member, "board": board, "lists": lists, "list_types": list_types}
    return render(request, "boards/board_lists.html", replacements)


# Delete a board
@member_required
def delete(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)

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

    # Show fetch form
    if request.method == "GET":
        replacements = {"member": member, "board": board}
        return render(request, "boards/fetch.html", replacements)

    # Confirm fetch form
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        start_time = time.time()
        board_fetcher = BoardFetcher(board)
        board_fetcher.fetch()
        end_time = time.time()
        print("Elapsed time {0} s".format(end_time-start_time))
        return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))

    raise Http404


# View card report
@login_required
def view_card_report(request, board_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
    cards = board.cards.all()
    replacements = {
        "member": member, "board": board, "cards": cards,
        "avg_lead_time": avg(cards, "lead_time"),
        "std_dev_lead_time": std_dev(cards, "lead_time"),
        "avg_cycle_time": avg(cards, "cycle_time"),
        "std_dev_cycle_time": std_dev(cards, "cycle_time"),
    }
    return render(request, "cards/list.html", replacements)


# View card
@login_required
def view_card(request, board_id, card_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        raise Http404

    comments = card.comments.all().order_by("-creation_datetime")
    labels = card.labels.all().order_by("name")

    replacements = {
        "member": member,
        "board": board,
        "card": card,
        "labels": labels,
        "comments": comments
    }
    return render(request, "cards/view.html", replacements)


# Export daily spent report in CSV format
@login_required
def export_card_report(request, board_id):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
    cards = board.cards.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = u'attachment; filename="{0}-cards.csv"'.format(board.name)

    csv_template = loader.get_template('cards/csv.txt')
    replacements = Context({
        "member": member,
        "board": board,
        "cards": cards,
        "avg_lead_time": avg(cards, "lead_time"),
        "std_dev_lead_time": std_dev(cards, "lead_time"),
        "avg_cycle_time": avg(cards, "cycle_time"),
        "std_dev_cycle_time": std_dev(cards, "cycle_time"),
    })
    response.write(csv_template.render(replacements))
    return response


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
    return render(request, "cards/workflow_card_report_list.html", replacements)


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
    return render(request, "labels/list.html", replacements)


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
    return render(request, "member_reports/list.html", replacements)


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
