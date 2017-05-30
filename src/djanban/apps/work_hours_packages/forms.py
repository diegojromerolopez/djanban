# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError

from djanban.apps.base.auth import get_member_boards
from djanban.apps.boards.models import Label
from djanban.apps.work_hours_packages.management.commands.notify_work_hours_package_completions import Command
from djanban.apps.work_hours_packages.models import WorkHoursPackage
from django import forms
from ckeditor.widgets import CKEditorWidget


# Work hours package filter
class WorkHoursPackageFilterForm(forms.Form):

    multiboard = forms.ChoiceField(label="Multiboard", choices=[], required=False)
    board = forms.ChoiceField(label="Board", choices=[], required=False)
    label = forms.ChoiceField(label="Label", choices=[], required=False)
    is_paid = forms.ChoiceField(label="Paid?", choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        super(WorkHoursPackageFilterForm, self).__init__(*args, **kwargs)

        # Available multiboards for the work hours package
        self.fields["multiboard"].choices = [("", "None")] + [
            (multiboard.id, multiboard.name) for multiboard in
            self.member.multiboards.all().order_by("name")
        ]

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
        self.fields["is_paid"].choices = [("", "Indiferent"),("Yes", "Yes"),("No", "No")]

    def clean(self):
        cleaned_data = super(WorkHoursPackageFilterForm, self).clean()
        return cleaned_data

    def get_work_hours_packages(self):
        # Filtering by multiboard, board or label
        multiboard_id = id=self.cleaned_data.get("multiboard")
        board_id = self.cleaned_data.get("board")
        label_id = self.cleaned_data.get("label")
        work_hours_packages = self.member.work_hours_packages.all().order_by("start_work_date", "end_work_date", "name")
        if multiboard_id:
            multiboard = self.member.multiboards.get(id=multiboard_id)
            work_hours_packages = work_hours_packages.filter(board__in=[board.id for board in multiboard.boards.all()])
        elif board_id:
            work_hours_packages = work_hours_packages.filter(board_id=board_id)
        elif label_id:
            label = Label.objects.get(id, board__in=get_member_boards(self.member))
            work_hours_packages = work_hours_packages.filter(board__label=label)

        # Filtering paid work hours packages
        if self.cleaned_data.get("is_paid") == "Yes" or self.cleaned_data.get("is_paid") == "No":
            work_hours_packages = work_hours_packages.filter(is_paid=(self.cleaned_data.get("is_paid") == "Yes"))

        return work_hours_packages


# Work hours package form
class WorkHoursPackageForm(forms.ModelForm):
    class Meta:
        model = WorkHoursPackage
        fields = [
            "type",
            "board", "multiboard", "label",
            "name", "description", "number_of_hours",
            "offset_hours", "offset_hours_description",
            "start_work_date", "end_work_date",
            "members", "is_paid", "payment_date",
            "notify_on_completion", "notification_email"
        ]
        widgets = {
            'start_work_date': forms.SelectDateWidget(),
            'end_work_date': forms.SelectDateWidget(empty_label=u"Until now"),
            'payment_date': forms.SelectDateWidget(empty_label=u"Not paid"),
        }

    class Media:
        css = {
            'all': ('css/work_hours_packages/form.css',)
        }
        js = (
            'js/work_hours_packages/form.js',
        )

    def __init__(self, *args, **kwargs):
        current_member = kwargs.pop("member")
        super(WorkHoursPackageForm, self).__init__(*args, **kwargs)
        self.fields["description"].widget = CKEditorWidget()

        # Available multiboards for the work hours package
        self.fields["multiboard"].choices = [("", "None")] + [
            (multiboard.id, multiboard.name) for multiboard in
            current_member.multiboards.all().order_by("name")
        ]

        # Available boards for this user
        boards = get_member_boards(current_member).filter(is_archived=False).order_by("name")
        self.fields["board"].choices = [("", "None")] + [
            (board.id, board.name)
            for board in boards
        ]

        # Available labels for this user
        self.fields["label"].choices = [("None", [("", "None")])] + [
            (board.name, [
                (label.id, label.name) for label in board.labels.exclude(name="").order_by("name")
                ]
            )
            for board in boards
        ]

        # Available members for the work hours package
        self.fields["members"].choices = [
            (member.id, member.external_username) for member in current_member.team_mates
        ]

    # Check consistency properties of a work hours package
    def clean(self):
        cleaned_data = super(WorkHoursPackageForm, self).clean()
        if (not cleaned_data.get("board") and not cleaned_data.get("label") and not cleaned_data.get("multiboard")) or\
           (cleaned_data.get("board") and cleaned_data.get("label") and cleaned_data.get("multiboard")) or\
           (cleaned_data.get("board") and cleaned_data.get("label")) or\
           (cleaned_data.get("board") and cleaned_data.get("multiboard")) or\
           (cleaned_data.get("label") and cleaned_data.get("multiboard")):
            raise ValidationError(
                "Please, select a board, label or multiboard. A package must be associated to one of them."
            )
        # Check if type matches with what we have selected
        if cleaned_data.get("type") == "board" and not cleaned_data.get("board"):
            raise ValidationError(u"Please, select a board for this work hours package")
        if cleaned_data.get("type") == "multiboard" and not cleaned_data.get("multiboard"):
            raise ValidationError(u"Please, select a multiboard for this work hours package")
        if cleaned_data.get("type") == "label" and not cleaned_data.get("label"):
            raise ValidationError(u"Please, select a label for this work hours package")

        # Erase elements not required depending on selected type
        if cleaned_data.get("type") == "board":
            cleaned_data["multiboard"] = None
            cleaned_data["label"] = None

        elif cleaned_data.get("type") == "multiboard":
            cleaned_data["board"] = None
            cleaned_data["label"] = None

        elif cleaned_data.get("type") == "label":
            cleaned_data["board"] = None
            cleaned_data["multiboard"] = None

        return cleaned_data

    def save(self, commit=True):
        super(WorkHoursPackageForm, self).save(commit=commit)
        if commit:
            if not self.instance.members.filter(id=self.instance.creator.id).exists():
                self.instance.members.add(self.instance.creator)


# Sent completion notifications form
class NotificationCompletionSenderForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to send completion notifications")

    def __init__(self, *args, **kwargs):
        self.member = kwargs.pop("member")
        super(NotificationCompletionSenderForm, self).__init__(*args, **kwargs)

    def send(self):
        command = Command()
        command.handle()


# Delete work hours package form
class DeleteWorkHoursPackageForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this work hours package")