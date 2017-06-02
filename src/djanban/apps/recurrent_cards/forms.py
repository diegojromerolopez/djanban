# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django import forms

from djanban.apps.base.auth import get_member_boards
from djanban.apps.boards.models import Label
from djanban.apps.recurrent_cards.models import WeeklyRecurrentCard


# Work hours package filter
class RecurrentCardFilterForm(forms.Form):

    label = forms.ChoiceField(label="Label", choices=[], required=False)
    is_active = forms.ChoiceField(label="Paid?", choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        self.board = kwargs.pop("board")
        super(RecurrentCardFilterForm, self).__init__(*args, **kwargs)

        # Available labels for this user
        self.fields["label"].choices = [("", "None")] + [
            (label.id, label.name) for label in self.board.labels.exclude(name="").order_by("name")]

        # Is paid?
        self.fields["is_active"].choices = [("", "Indiferent"),("Yes", "Yes"),("No", "No")]

    def clean(self):
        cleaned_data = super(RecurrentCardFilterForm, self).clean()
        return cleaned_data

    def get_recurrent_cards(self):
        # Filtering by board or label
        board_id = self.cleaned_data.get("board")
        label_id = self.cleaned_data.get("label")
        recurrent_cards = self.member.recurrent_cards.all().order_by("board", "name")
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
            "name", "description", "position", "estimated_time", "creation_list",
            "labels", "members",
            "create_on_mondays", "create_on_tuesdays", "create_on_wednesdays", "create_on_thursdays",
            "create_on_fridays", "create_on_saturdays", "create_on_sundays", "move_to_list_when_day_ends",
            "is_active"
        ]

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        self.board = kwargs.pop("board")
        super(WeeklyRecurrentCardForm, self).__init__(*args, **kwargs)

        # Lists of this board
        active_lists = [(list_.id, list_.name) for list_ in self.board.active_lists.order_by("position")]
        self.fields["creation_list"].choices = active_lists
        self.fields["move_to_list_when_day_ends"].choices = [("", "None")] + active_lists

        # Member team mates of this user
        self.fields["members"].choices =\
            [(member.id, member.external_username) for member in self.member.team_mates.all()]

        # Available labels for this board
        self.fields["labels"].choices = \
            [("", "None")] +\
            [(label.id, label.name) for label in self.board.labels.exclude(name="").order_by("name")]

    def save(self, commit=True):
        super(WeeklyRecurrentCardForm, self).save(commit)
        if commit:
            # Add the creator as member by default
            if not self.instance.members.filter(id=self.instance.creator.id).exists():
                self.instance.members.add(self.instance.creator)


# Delete recurrent card
class DeleteWeeklyRecurrentCardForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this recurrent card")