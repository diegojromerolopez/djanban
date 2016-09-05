# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType

from djangotrellostats.apps.repositories.models import GitLabRepository, Commit


def get_form_class(repository):
    derived_type = repository.type
    if derived_type == ContentType.objects.get_for_model(type(repository.derived_object)):
        return GitLabRepositoryForm
    raise NotImplementedError(u"There is only one type of repository")


class GitLabRepositoryForm(forms.ModelForm):
    class Meta:
        model = GitLabRepository
        fields = ["name", "description", "url", "access_token", "project_name"]

    def save(self, commit=True):
        super(GitLabRepositoryForm, self).save(commit=False)
        if commit:
            self.instance.type = ContentType.objects.get_for_model(type(self.instance))
            self.instance.save()
        return self.instance




class DeleteRepositoryForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this repository")


class CommitForm(forms.ModelForm):
    class Meta:
        model = Commit
        fields = ["commit", "comments"]

    def save(self, commit=True):
        super(CommitForm, self).save(commit=False)
        if commit:
            commit_info = self.instance.repository.fetch_commit(self.cleaned_data["commit"])
            self.instance.code = commit_info["code"]
            self.instance.creation_datetime = commit_info["creation_datetime"]
            self.instance.save()
        return self.instance




class DeleteCommitForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this commit")
