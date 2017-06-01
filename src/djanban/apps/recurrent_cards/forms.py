# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django import forms

from djanban.apps.base.auth import get_member_boards
from djanban.apps.boards.models import Label
from djanban.apps.recurrent_cards.models import WeeklyRecurrentCard


# Work hours package filter
class RecurrentCardFilterForm(forms.Form):

    board = forms.ChoiceField(label="Board", choices=[], required=False)
    label = forms.ChoiceField(label="Label", choices=[], required=False)
    is_active = forms.ChoiceField(label="Paid?", choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        super(RecurrentCardFilterForm, self).__init__(*args, **kwargs)

        # Available boards for this user
        boards = get_member_boards(self.member).filter(is_archived=False).order_by("name")
        self.fields["board"].choices = [("", "None")] + [
            (board.id, board.name)
            for board in boards
        ]

        # Available labels for this user
        self.fields["label"].choices = [("None", [("", "None")])] + [
            (board.name, [(label.id, label.name) for label in board.labels.exclude(name="").order_by("name")])
            for board in boards
        ]

        # Is paid?
        self.fields["is_active"].choices = [("", "Indiferent"),("Yes", "Yes"),("No", "No")]

    def clean(self):
        cleaned_data = super(RecurrentCardFilterForm, self).clean()
        return cleaned_data

    def get_recurrent_cards(self):
        # Filtering by board or label
        board_id = self.cleaned_data.get("board")
        label_id = self.cleaned_data.get("label")
        recurrent_cards = self.member.work_hours_packages.all().order_by("board", "name")
        if board_id:
            recurrent_cards = recurrent_cards.filter(board_id=board_id)
        elif label_id:
            label = Label.objects.get(id, board__in=get_member_boards(self.member))
            recurrent_cards = recurrent_cards.filter(board__label=label)

        # Filtering paid work hours packages
        if self.cleaned_data.get("is_active") == "Yes" or self.cleaned_data.get("is_active") == "No":
            recurrent_cards = recurrent_cards.filter(is_paid=(self.cleaned_data.get("is_active") == "Yes"))

        return recurrent_cards


class WeeklyRecurrentCardForm(forms.ModelForm):
    class Meta:
        model = WeeklyRecurrentCard
        fields = [
            "board", "name", "description", "position", "estimated_time", "creation_list",
            "labels", "members", "is_active",
            "create_on_mondays", "create_on_tuesdays", "create_on_wednesdays", "create_on_thursdays",
            "create_on_fridays", "create_on_saturdays", "create_on_sundays", "deadline", "move_on_deadline_to_list"
        ]

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        super(WeeklyRecurrentCardForm, self).__init__(*args, **kwargs)

        # Available boards for this member
        boards = get_member_boards(self.member).filter(is_archived=False).order_by("name")
        self.fields["board"].choices = [("", "None")] + [
            (board.id, board.name)
            for board in boards
        ]

        # Available labels for this user
        self.fields["label"].choices = [("None", [("", "None")])] + [
            (board.name, [(label.id, label.name) for label in board.labels.exclude(name="").order_by("name")])
            for board in boards
        ]


# Delete recurrent card
class DeleteWeeklyRecurrentCardForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this recurrent card")