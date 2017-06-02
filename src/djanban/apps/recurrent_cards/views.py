# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from djanban.apps.base.auth import user_is_member, user_is_administrator, get_user_boards
from djanban.apps.base.decorators import member_required
from djanban.apps.base.views import models as model_views
from djanban.apps.boards.models import Board
from djanban.apps.recurrent_cards.forms import WeeklyRecurrentCardForm, DeleteWeeklyRecurrentCardForm, \
    RecurrentCardFilterForm
from djanban.apps.recurrent_cards.models import WeeklyRecurrentCard


# New recurrent card
@member_required
def new(request, board_id):
    member = _get_user_member_or_none(request.user)
    board = _get_user_board(request.user, board_id)
    work_hours_package = WeeklyRecurrentCard(creator=member, board=board)
    return model_views.new(
        request, instance=work_hours_package,
        form_class=WeeklyRecurrentCardForm, extra_form_parameters={"member": member, "board": board},
        template_path="recurrent_cards/new.html",
        ok_url=reverse("boards:recurrent_cards:view_list", args=(board_id,))
    )


# Edition of a work hours package
@member_required
def edit(request, board_id, recurrent_card_id):
    member = _get_user_member_or_none(request.user)
    board = _get_user_board(request.user, board_id)
    recurrent_card = _get_recurrent_card(request.user, board, recurrent_card_id)

    return model_views.edit(
        request, instance=recurrent_card,
        form_class=WeeklyRecurrentCardForm, extra_form_parameters={"member": member, "board": board},
        template_path="recurrent_cards/edit.html",
        ok_url=reverse("boards:recurrent_cards:view_list", args=(board_id,))
    )


# View a work hours package
@login_required
def view(request, board_id, recurrent_card_id):
    member = _get_user_member_or_none(request.user)
    board = _get_user_board(request.user, board_id)
    recurrent_card = _get_recurrent_card(request.user, board, recurrent_card_id)

    replacements = {"recurrent_card": recurrent_card, "member": member, "board": board}
    return render(request, "recurrent_cards/view.html", replacements)


# View all work hours packages
@login_required
def view_list(request, board_id):
    member = _get_user_member_or_none(request.user)
    board = _get_user_board(request.user, board_id)
    form = None
    recurrent_cards = WeeklyRecurrentCard.objects.none()
    if member:
        form = RecurrentCardFilterForm(request.GET, member=member, board=board)

    if form and form.is_valid():
        recurrent_cards = form.get_recurrent_cards()
    else:
        if user_is_administrator(request.user):
            recurrent_cards = WeeklyRecurrentCard.objects.filter(board=board).order_by("name")
        elif member:
            recurrent_cards = member.recurrent_cards.filter(board=board).order_by("name")

    replacements = {"recurrent_cards": recurrent_cards, "member": member, "board": board, "form": form}
    return render(request, "recurrent_cards/list.html", replacements)


# Delete a work hours package
@login_required
def delete(request, board_id, recurrent_card_id):
    member = _get_user_member_or_none(request.user)
    board = _get_user_board(request.user, board_id)
    recurrent_card = _get_recurrent_card(request.user, board, recurrent_card_id)

    return model_views.delete(
        request, instance=recurrent_card, form_class=DeleteWeeklyRecurrentCardForm,
        next_url=reverse("boards:recurrent_cards:view_list", args=(board_id,)),
        template_path="recurrent_cards/delete.html",
        template_replacements={"member": member, "board": board}
    )


# Get the recurrent card
def _get_recurrent_card(current_user, board, recurrent_card_id):
    try:
        if user_is_administrator(current_user):
            return WeeklyRecurrentCard.objects.get(board=board, id=recurrent_card_id)
        elif user_is_member(current_user):
            member = current_user.member
            return member.created_recurrent_cards.get(board=board, id=recurrent_card_id)
        else:
            raise Http404
    except WeeklyRecurrentCard.DoesNotExist:
        raise Http404


# Get the board
def _get_user_board(current_user, board_id):
    try:
        return get_user_boards(current_user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404


# Get user member or None
def _get_user_member_or_none(current_user):
    if user_is_member(current_user):
        return current_user.member
    return None
