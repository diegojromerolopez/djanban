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
        fields = ["name", "description", "is_archived", "order", "boards"]

    def __init__(self, *args, **kwargs):
        super(MultiboardForm, self).__init__(*args, **kwargs)
        self.fields["description"].widget = CKEditorWidget()
        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        self.fields["boards"].choices = [(board.id, board.name) for board in get_user_boards(current_user).order_by("name")]

# Delete multiboard form
class DeleteMultiboardForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this multiboard")
