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



