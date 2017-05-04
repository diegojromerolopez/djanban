# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from ckeditor.widgets import CKEditorWidget
from django import forms

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.multiboards.models import Multiboard
from crequest.middleware import CrequestMiddleware


# Multiboard form
class MultiboardForm(forms.ModelForm):
    class Meta:
        model = Multiboard
        fields = [
            "name", "description", "is_archived", "order", "boards",
            # Inform if the multiboard must be shown in index
            "show_in_index",
            # Inform if the tasks of the following statuses must be shown
            "show_backlog_tasks",
            "show_ready_to_develop_tasks",
            "show_development_tasks",
            "show_after_development_in_review_tasks",
            "show_after_development_waiting_release_tasks",
            "show_done_tasks"
        ]

    def __init__(self, *args, **kwargs):
        super(MultiboardForm, self).__init__(*args, **kwargs)
        self.fields["description"].widget = CKEditorWidget()
        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        self.fields["boards"].choices = [(board.id, board.name) for board in get_user_boards(current_user).order_by("name")]


# Delete multiboard form
class DeleteMultiboardForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this multiboard")
