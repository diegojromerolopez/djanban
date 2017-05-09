# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import shortuuid

from ckeditor.widgets import CKEditorWidget
from dal import autocomplete

from django import forms
from django.utils import timezone

from djanban.apps.journal.models import JournalEntry, JournalEntryTag
from django.template.defaultfilters import slugify


# Journal entry form
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ["title", "content", "tags"]

    # Django autocomplete light widget
    tags = forms.ModelMultipleChoiceField(
         label=u"Journal entry tags",
         required=False,
         queryset=JournalEntryTag.objects.all().order_by("name"),
         widget=autocomplete.ModelSelect2Multiple(url='boards:journal_entry-tag-autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(JournalEntryForm, self).__init__(*args, **kwargs)
        #self.fields["content"].widget = CKEditorWidget(config_name="full")


# New journal entry form
class NewJournalEntryForm(JournalEntryForm):
    class Meta:
        model = JournalEntry
        fields = ["title", "content", "tags"]

    def __init__(self, *args, **kwargs):
        super(NewJournalEntryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        now = timezone.now()
        self.instance.creation_datetime = now
        self.instance.last_update_datetime = now
        self.instance.uuid = shortuuid.ShortUUID().random(length=16).lower()
        self.instance.slug = "{0}-{1}".format(slugify(self.instance.title)[0:112], self.instance.uuid)
        super(NewJournalEntryForm, self).save(commit=False)
        if commit:
            self.instance.save()
            self.save_m2m()
            return self.instance


# Edit journal entry form
class EditJournalEntryForm(JournalEntryForm):
    class Meta:
        model = JournalEntry
        fields = ["title", "content", "tags"]


# Requirement form
class DeleteJournalEntryForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this journal entry")