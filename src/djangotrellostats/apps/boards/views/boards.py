# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render
from djangotrellostats.apps.boards.models import List


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


# Delete a board
@login_required
def fetch_cards(request, board_id):
    member = request.user.member
    board = member.boards.get(id=board_id)
    confirmed_board_id = request.POST.get("board_id")
    if confirmed_board_id and confirmed_board_id == board_id:
        board.fetch_cards()
        return HttpResponseRedirect(reverse("boards:view_boards"))
    raise Http404


# Change list type. Remember a list can be "development" or "done" list
@login_required
def change_list_type(request):
    member = request.user.member
    if request.method == "POST":
        list_id = request.POST.get("list_id", board__member=member)
        type_ = request.POST.get("type")
        if type_ not in List.LIST_TYPES:
            raise Http404
        list_ = List.objects.get(id=list_id)
        list_.type = type_
        list_.save()
        return HttpResponseRedirect(reverse("boards:view_board_lists", args=(list_.board_id,)))
    raise Http404
