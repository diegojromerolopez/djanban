# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
from django import forms
from django.core.validators import MinValueValidator
from django.db import transaction
from django.forms import models
from djangotrellostats.apps.boards.models import Board

from trello.board import Board as TrelloBoard

# Board edition form
from djangotrellostats.apps.fetch.fetchers.trello import Initializer


class EditBoardForm(models.ModelForm):
    class Meta:
        model = Board
        fields = ["has_to_be_fetched", "comments", "estimated_number_of_hours",
                  "percentage_of_completion", "hourly_rates",
                  "enable_public_access", "public_access_code", "show_on_slideshow"]

    def __init__(self, *args, **kwargs):
        super(EditBoardForm, self).__init__(*args, **kwargs)
        self.fields["hourly_rates"].help_text = u"Please, select the hourly rates this board uses. System does not " \
                                                u"check if there is overlapping, so take care."

    def clean(self):
        cleaned_data = super(EditBoardForm, self).clean()
        return cleaned_data


# Board creation form
class NewBoardForm(models.ModelForm):
    class Meta:
        model = Board
        fields = ["name", "description"]

    #name = forms.CharField(label=u"Name of the new board")

    #description = forms.CharField(label=u"Name of the new board", widget=forms.Textarea(), required=False)

    def __init__(self, *args, **kwargs):
        super(NewBoardForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(NewBoardForm, self).clean()
        return cleaned_data

    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                #board = Board(name=self.cleaned_data.get("name"), description=self.cleaned_data.get("description"))
                board = self.instance
                initializer = Initializer(member=self.instance.creator)
                initializer.create_board(board)
                super(NewBoardForm, self).save(commit=True)



