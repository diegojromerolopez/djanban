# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http.response import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.template.context import Context

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.forms import NewCardForm
from djangotrellostats.apps.boards.models import List, Board, Card, CardComment
from djangotrellostats.apps.boards.stats import avg, std_dev


# Create a new card
@member_required
def new(request, board_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    card = Card(board=board, list=board.first_list)
    card.member = member

    if request.method == "POST":
        form = NewCardForm(request.POST, instance=card)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:view", args=(board_id,)))
    else:
        form = NewCardForm(instance=card)

    return render(request, "cards/new.html", {"form": form, "board": board, "member": member})


# Move this card forward
@member_required
def move_forward(request, board_id, card_id):
    return _move(request, board_id, card_id, movement_type="forward")


# Move this card back
@member_required
def move_backward(request, board_id, card_id):
    return _move(request, board_id, card_id, movement_type="backward")


# Move this card
def _move(request, board_id, card_id, movement_type="forward"):
    if request.method != "POST":
        raise Http404

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        raise Http404

    if movement_type == "forward":
        card.move_forward(member)
    elif movement_type == "backward" or movement_type == "back":
        card.move_backward(member)
    else:
        raise Http404

    return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))


# Add new comment to a card
@member_required
def add_comment(request, board_id, card_id):
    if request.method != "POST":
        raise Http404
    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        raise Http404

    # Getting the comment content
    comment_content = request.POST.get("comment")

    # If the comment is empty, redirect to card view
    if not comment_content:
        return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))

    # Otherwise, add the comment
    card.add_comment(member, comment_content)
    return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))


# Delete comment of a card
@member_required
def delete_comment(request, board_id, card_id, comment_id):
    if request.method != "POST":
        raise Http404
    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        comment = card.comments.get(id=comment_id)
    except (Board.DoesNotExist, Card.DoesNotExist, CardComment.DoesNotExist) as e:
        raise Http404

    # Delete the comment
    card.delete_comment(member, comment)
    return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))


# Add new spent/estimated time measurement
@member_required
def add_spent_estimated_time(request, board_id, card_id):
    if request.method != "POST":
        raise Http404

    member = request.user.member
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
    except (Board.DoesNotExist, Card.DoesNotExist) as e:
        raise Http404

    # Getting the date
    selected_date = request.POST.get("date")

    # Getting spent and estimated time
    spent_time = request.POST.get("spent_time")
    estimated_time = request.POST.get("estimated_time")

    # If the description is not present, get the name of tha card as description
    description = request.POST.get("description", card.name)
    if not description:
        description = card.name

    # Checking if spent time and estimated time floats
    if spent_time != "":
        try:
            spent_time = float(spent_time.replace(",", "."))
        except ValueError:
            raise Http404
    else:
        spent_time = None

    if estimated_time != "":
        try:
            estimated_time = float(estimated_time.replace(",", "."))
        except ValueError:
            raise Http404
    else:
        estimated_time = None

    if spent_time is None and estimated_time is None:
        raise Http404

    # Optional days ago parameter
    days_ago = None
    matches = re.match(r"^\-(?P<days_ago>\d+)$", selected_date)
    if matches:
        days_ago = int(matches.group("days_ago"))

    card.add_spent_estimated_time(member, spent_time, estimated_time, days_ago=days_ago, description=description)
    return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))


# View card
@login_required
def view(request, board_id, card_id):
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
    card_list = card.list

    try:
        previous_list = card_list.previous_list
    except List.DoesNotExist:
        previous_list = None

    try:
        next_list = card_list.next_list
    except List.DoesNotExist:
        next_list = None

    replacements = {
        "member": member,
        "board": board,
        "card": card,
        "members": card.members.all().order_by("initials"),
        "list": card_list,
        "next_list": next_list,
        "previous_list": previous_list,
        "labels": labels,
        "comments": comments
    }
    return render(request, "cards/view.html", replacements)


# View card report
@login_required
def view_report(request, board_id):
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


# Export daily spent report in CSV format
@login_required
def export_report(request, board_id):
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
