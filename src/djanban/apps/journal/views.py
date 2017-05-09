# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from dal import autocomplete

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from djanban.apps.base.auth import user_is_member, get_user_boards
from djanban.apps.base.decorators import member_required
from djanban.apps.boards.models import Board
from djanban.apps.journal.forms import NewJournalEntryForm, EditJournalEntryForm, DeleteJournalEntryForm
from djanban.apps.journal.models import JournalEntry, JournalEntryTag


# Journal
@login_required
def view(request, board_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member

    board = get_object_or_404(Board, id=board_id)

    journal_entry_filter = {}
    # Filter by author
    author_get_param = request.GET.get("author")
    if request.GET.get("author") and board.members.filter(Q(trello_member__username=author_get_param)|Q(username=author_get_param)).exists():
        journal_entry_filter["author"] = board.members.filter(Q(trello_member__username=author_get_param)|Q(username=author_get_param))
    # Filter by tag
    if request.GET.get("tag"):
        journal_entry_filter["tags__name"] = request.GET.get("tag")

    journal_entries = board.journal_entries.filter(**journal_entry_filter).order_by("-creation_datetime")

    replacements = {
        "member": member,
        "board": board,
        "journal_entries": journal_entries
    }
    return render(request, "journal/view.html", replacements)


# View a journal entry
@login_required
def view_entry(request, board_id, year, month, journal_entry_slug):
    try:
        member = None
        if user_is_member(request.user):
            member = request.user.member
        board = get_user_boards(request.user).get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    journal_entry = get_object_or_404(
        JournalEntry, creation_datetime__year=year, creation_datetime__month=month, slug=journal_entry_slug
    )

    replacements = {
        "member": member,
        "board": board,
        "tags": journal_entry.tags.all().order_by("name"),
        "year": year,
        "month": month,
        "journal_entry": journal_entry
    }
    return render(request, "journal/entries/view.html", replacements)


# New journal entry
@member_required
def new_entry(request, board_id):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    journal_entry = JournalEntry(board=board, author=member)

    if request.method == "POST":
        form = NewJournalEntryForm(request.POST, instance=journal_entry)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:journal:view", args=(board_id,)))
    else:
        form = NewJournalEntryForm(instance=journal_entry)

    return render(request, "journal/entries/new.html", {"form": form, "board": board, "member": member})


# Edit journal entry
@member_required
def edit_entry(request, board_id, year, month, journal_entry_slug):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except Board.DoesNotExist:
        raise Http404

    journal_entry = get_object_or_404(
        JournalEntry, creation_datetime__year=year, creation_datetime__month=month, slug=journal_entry_slug
    )

    if request.method == "POST":
        form = EditJournalEntryForm(request.POST, instance=journal_entry)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("boards:journal:view", args=(board_id,)))
    else:
        form = EditJournalEntryForm(instance=journal_entry)

    replacements = {"form": form, "board": board, "member": member, "journal_entry": journal_entry}
    return render(request, "journal/entries/edit.html", replacements)


# Delete a journal entry
@member_required
def delete_entry(request, board_id, year, month, journal_entry_slug):
    member = request.user.member
    try:
        board = member.boards.get(id=board_id)
    except ObjectDoesNotExist:
        raise Http404

    journal_entry = get_object_or_404(
        JournalEntry, creation_datetime__year=year, creation_datetime__month=month, slug=journal_entry_slug
    )

    if request.method == "POST":
        form = DeleteJournalEntryForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            journal_entry.delete()
            return HttpResponseRedirect(reverse("boards:journal:view", args=(board_id,)))

    else:
        form = DeleteJournalEntryForm()

    replacements = {"form": form, "board": board, "member": member, "journal_entry": journal_entry}
    return render(request, "journal/entries/delete.html", replacements)


# Class-based view that returns tags that match with the one written by user
class JournalEntryTagAutocompleteView(autocomplete.Select2QuerySetView):
    # Only members can create tags
    def has_add_permission(self, request):
        return user_is_member(request.user)

    def get_queryset(self):
        qs = JournalEntryTag.objects.all().order_by("name")
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
