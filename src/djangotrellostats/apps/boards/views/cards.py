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
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.forms import NewCardForm, WeekSummaryFilterForm
from djangotrellostats.apps.boards.models import List, Board, Card, CardComment, Label, CardAttachment
from djangotrellostats.apps.boards.stats import avg, std_dev
from djangotrellostats.apps.forecasters.serializer import CardSerializer
from djangotrellostats.utils.week import get_iso_week_of_year, get_week_of_year


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

    return render(request, "boards/cards/new.html", {"form": form, "board": board, "member": member})


# Change labels of this card
@member_required
def change_labels(request, board_id, card_id):
    if request.method != "POST":
        raise Http404

    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
        card = board.cards.get(id=card_id)
    except Board.DoesNotExist:
        raise Http404

    # Get in labels a list of objects Label gotten from the selected labels
    labels = []
    label_ids = request.POST.getlist("labels")
    for label_id in label_ids:
        try:
            label = board.labels.exclude(name="").get(id=label_id)
            labels.append(label)
        except Label.DoesNotExist:
            pass

    card.update_labels(member, labels)

    return HttpResponseRedirect(reverse("boards:view_card", args=(board_id, card_id)))


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


# Download card attachment
@member_required
def download_attachment(request, board_id, card_id, attachment_id):
    if request.method != "GET":
        raise Http404
    try:
        board = get_user_boards(request.user).get(id=board_id)
        card = board.cards.get(id=card_id)
        attachment = card.attachments.get(id=attachment_id)
    except (Board.DoesNotExist, Card.DoesNotExist, CardAttachment.DoesNotExist) as e:
        raise Http404

    print attachment.file
    if not attachment.file:
        print "sdfasfs"
        attachment.fetch_external_file()

    return HttpResponseRedirect(attachment.file.url)


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
    return HttpResponseRedirect(reverse("boards:view_taskboard", args=(board_id, "/card/{0}".format(card_id))))


@login_required
def view_short_url(request, board_id, card_uuid):
    board = get_user_boards(request.user).get(id=board_id)
    card = board.cards.get(uuid=card_uuid)
    return HttpResponseRedirect(reverse("boards:view_taskboard", args=(board.id,"/card/{0}".format(card.id))))


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
        "week_of_year": get_week_of_year(),
        "member": member, "board": board, "cards": cards,
        "avg_lead_time": avg(cards, "lead_time"),
        "std_dev_lead_time": std_dev(cards, "lead_time"),
        "avg_cycle_time": avg(cards, "cycle_time"),
        "std_dev_cycle_time": std_dev(cards, "cycle_time"),
    }
    return render(request, "boards/cards/list.html", replacements)


# Export card report in CSV format
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

    csv_template = loader.get_template('boards/cards/csv.txt')
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


# Export detailed card report in CSV format
@login_required
def export_detailed_report(request, board_id):
    try:
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404
    cards = board.cards.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = u'attachment; filename="{0}-detailed-card-report.csv"'.format(board.name)

    csv_template = loader.get_template('boards/cards/detailed_report_csv.txt')
    members = board.members.all()
    card_list = []
    for card in cards:
        serialized_card = CardSerializer(card, members).serialize()
        serialized_card["id"] = card.id
        card_list.append(serialized_card)

    replacements = Context({
        "cards": card_list,
    })
    response.write(csv_template.render(replacements))
    return response


# View week report
@login_required
def view_week_summary(request, board_id, member_id="all", week_of_year=None):
    try:
        current_member = None
        if user_is_member(request.user):
            current_member = request.user.member
        board = get_user_boards(request.user).get(id=board_id, is_archived=False)
    except Board.DoesNotExist:
        raise Http404

    replacements = {"board": board, "member": current_member}

    if request.method == "POST":
        form = WeekSummaryFilterForm(post_data=request.POST, board=board)
        if form.is_valid():
            year = form.cleaned_data.get("year")
            week = form.cleaned_data.get("week")
            member_id = form.cleaned_data.get("member")
            week_of_year = "{0}W{1}".format(year, week)
            return HttpResponseRedirect(reverse("boards:view_week_summary", args=(board_id, member_id, week_of_year,)))

    year = None
    week = None

    if week_of_year is None:
        now = timezone.now()
        year = now.year
        week = int(get_iso_week_of_year(now))
        week_of_year = "{0}W{1}".format(year, week)

    if week is None or year is None:
        matches = re.match(r"^(?P<year>\d{4})W(?P<week>\d{2})$", week_of_year)
        if matches:
            year = int(matches.group("year"))
            week = int(matches.group("week"))

    form = WeekSummaryFilterForm(initial={"year": year, "week": week, "member": member_id}, board=board)
    replacements["form"] = form
    replacements["week_of_year"] = week_of_year

    # Done cards that are of this member
    member_filter = {}
    if member_id != "all":
        member_filter = {"members": member_id}

    # Date limits of the selected week
    week_start_date = Week(year, week).monday()
    week_end_date = Week(year, week).friday()

    # Getting the cards that were completed in the selected week for the selected user
    completed_cards = board.cards.\
        filter(list__type="done",
               movements__type="forward",
               movements__destination_list__type="done",
               movements__datetime__gte=week_start_date,
               movements__datetime__lte=week_end_date)\
        .filter(**member_filter).\
        order_by("last_activity_datetime")

    replacements["completed_cards"] = completed_cards

    # Time spent developing on this week
    if member_id == "all":
        spent_time = board.get_spent_time([week_start_date, week_end_date])
        adjusted_spent_time = board.get_spent_time([week_start_date, week_end_date])
    else:
        member = board.members.get(id=member_id)
        spent_time = board.get_spent_time([week_start_date, week_end_date], member)
        adjusted_spent_time = board.get_spent_time([week_start_date, week_end_date], member)
        replacements["selected_member"] = member

    replacements["spent_time"] = spent_time
    replacements["adjusted_spent_time"] = adjusted_spent_time

    replacements["week_start_date"] = week_start_date
    replacements["week_end_date"] = week_end_date

    return render(request, "boards/week_summary.html", replacements)