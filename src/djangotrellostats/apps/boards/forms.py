# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from crequest.middleware import CrequestMiddleware
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import models
from django.utils import timezone

from djangotrellostats.apps.boards.models import Board, Card, List
from djangotrellostats.apps.fetch.fetchers.trello.boards import Initializer
from djangotrellostats.apps.members.models import MemberRole

from djangotrellostats.utils.custom_uuid import custom_uuid
from djangotrellostats.utils.week import get_iso_week_of_year


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
                if self.instance.creator.has_trello_profile:
                    initializer = Initializer(member=self.instance.creator)
                    lists = self.cleaned_data.get("lists")
                    initializer.create_board(self.instance, lists=lists)
                    super(NewBoardForm, self).save(commit=True)
                else:
                    self.instance.uuid = custom_uuid()
                    self.instance.has_to_be_fetched = False
                    self.instance.last_activity_datetime = timezone.now()
                    super(NewBoardForm, self).save(commit=True)
                    # Adding the creator as member of the board
                    self.instance.members.add(self.instance.creator)
                    # Adding the creator as admin of the board
                    role, created = MemberRole.objects.get_or_create(board=self.instance, type="admin")
                    role.members.add(self.instance.creator)
                    self.instance.roles.add(role)


# Deprecated: use new Full Board APP
# New list form
class NewListForm(models.ModelForm):
    class Meta:
        model = List
        fields = ["name", "type"]

    def save(self, commit=True):
        if commit:
            with transaction.atomic():
                # Getting the current member (current user)
                current_request = CrequestMiddleware.get_request()
                current_user = current_request.user
                if not hasattr(current_user, "member"):
                    raise AssertionError("Only members can create lists")

                current_member = current_user.member
                list_ = self.instance

                self.instance = self.instance.board.new_list(current_member, self.instance)

                # Create the list
                super(NewListForm, self).save(commit=True)

                # Clean cached charts for this lists' board
                list_.board.clean_cached_charts()


# Deprecated: use new Full Board APP
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
                board = self.instance.board
                list_ = self.instance.list

                # Getting the current member (current user)
                current_request = CrequestMiddleware.get_request()
                current_user = current_request.user
                if not hasattr(current_user, "member"):
                    raise AssertionError("Only members can create lists")

                current_member = current_user.member
                self.instance = list_.add_card(current_member, self.instance.name, position="bottom")

                self.instance.creation_datetime = timezone.now()
                self.instance.last_activity_datetime = timezone.now()
                # Create the card
                super(NewCardForm, self).save(commit=True)
                # Clean cached charts for this board
                board.clean_cached_charts()


# Week summary filter
# This filter filters the
class WeekSummaryFilterForm(forms.Form):
    year = forms.ChoiceField(label="Year", choices=[], required=True)
    week = forms.ChoiceField(label="Week", choices=[], required=True)
    member = forms.ChoiceField(label="Member", choices=[], required=True)

    def __init__(self, board, post_data=None, initial=None):
        super(WeekSummaryFilterForm, self).__init__(data=post_data, initial=initial)
        now = timezone.now()
        year = now.year

        working_start_date = board.get_working_start_date()
        working_end_date = board.get_working_end_date()
        if working_start_date and working_end_date:
            self.fields["year"].choices = [(year_i, year_i) for year_i in range(working_start_date.year, working_end_date.year+1)]

            if working_start_date.year == working_end_date.year:
                start_week = get_iso_week_of_year(working_start_date)
                end_week = get_iso_week_of_year(working_end_date)
                self.fields["week"].choices = [(week_i, week_i) for week_i in range(start_week, end_week+1)]
            else:
                self.fields["week"].choices = [(week_i, week_i) for week_i in range(1, 53 + 1)]
        else:
            self.fields["year"].choices = [(year_i, year_i) for year_i in range(year-100, year+101)]
            self.fields["week"].choices = [(week_i, week_i) for week_i in range(1, 53+1)]

        self.fields["member"].choices = [("all", "All")] +\
            [(member.id, member.external_username) for member in board.members.filter(is_developer=True)]

        if initial is None:
            self.initial["year"] = year
            self.initial["week"] = get_iso_week_of_year(now)
            self.initial["member"] = "all"
