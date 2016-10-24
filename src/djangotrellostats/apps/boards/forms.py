# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import transaction
from django.forms import models
from djangotrellostats.apps.boards.models import Board, Card
from djangotrellostats.apps.fetch.fetchers.trello import Initializer
from djangotrellostats.trello_api.cards import new_card


# Board edition form
class EditBoardForm(models.ModelForm):
    class Meta:
        model = Board
        fields = [
            "has_to_be_fetched", "comments", "estimated_number_of_hours",
            "percentage_of_completion", "hourly_rates",
            "enable_public_access", "public_access_code", "show_on_slideshow",
            "background_color", "title_color"
        ]

    def __init__(self, *args, **kwargs):
        super(EditBoardForm, self).__init__(*args, **kwargs)
        self.fields["hourly_rates"].help_text = u"Please, select the hourly rates this board uses. System does not " \
                                                u"check if there is overlapping, so take care."

        self.fields["background_color"].widget.attrs["class"] = "jscolor"
        self.fields["title_color"].widget.attrs["class"] = "jscolor"

    def clean_background_color(self):
        try:
            int(self.cleaned_data.get("background_color"), 16)
        except ValueError:
            raise ValidationError("Background color is not an hexadecimal number")
        return self.cleaned_data.get("background_color")

    def clean_title_color(self):
        try:
            int(self.cleaned_data.get("title_color"), 16)
        except ValueError:
            raise ValidationError("Title color is not an hexadecimal number")
        return self.cleaned_data.get("title_color")

    def clean(self):
        cleaned_data = super(EditBoardForm, self).clean()
        return cleaned_data


# Board creation form
class NewBoardForm(models.ModelForm):
    MAX_NUM_LISTS = 20

    class Meta:
        model = Board
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super(NewBoardForm, self).__init__(*args, **kwargs)
        for i in range(1, NewBoardForm.MAX_NUM_LISTS+1):
            self.fields["list_{0}".format(i)] = forms.CharField(
                label=u"List {0}".format(i),
                help_text=u"Name of list {0} in this new board. Optional.".format(i),
                required=False)

    def clean(self):
        cleaned_data = super(NewBoardForm, self).clean()
        list_names = []
        for i in range(1, NewBoardForm.MAX_NUM_LISTS+1):
            field_name = "list_{0}".format(i)
            field_value = cleaned_data.get(field_name)
            if field_value:
                list_names.append(field_value)
        cleaned_data["lists"] = list_names
        return cleaned_data

    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                initializer = Initializer(member=self.instance.creator)
                lists = self.cleaned_data.get("lists")
                initializer.create_board(self.instance, lists=lists)
                super(NewBoardForm, self).save(commit=True)


# New card
class NewCardForm(models.ModelForm):
    class Meta:
        model = Card
        fields = ["name", "description", "list", "labels"]

    def __init__(self, *args, **kwargs):
        super(NewCardForm, self).__init__(*args, **kwargs)
        board = self.instance.board

        # Only list of the same board are choices
        lists = board.lists.exclude(type="closed").order_by("position")
        self.fields["list"].choices = [(list_.id, list_.name) for list_ in lists]

        # Only labels of the same board are choices
        labels = board.labels.exclude(name="").order_by("name")
        self.fields["labels"].choices = [(label.id, label.name) for label in labels]

    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                card = self.instance
                # Call Trello API to create the card
                trello_card = new_card(card, card.member, self.cleaned_data.get("labels"))
                # Get TrelloCard attributes and assigned them to our new object Card
                card.uuid = trello_card.id
                card.short_url = trello_card.shortUrl
                card.url = trello_card.url
                card.position = trello_card.pos
                card.creation_datetime = timezone.now()
                card.last_activity_datetime = timezone.now()
                # Create the card
                super(NewCardForm, self).save(commit=True)
                # Clean cached charts for this board
                card.board.clean_cached_charts()

