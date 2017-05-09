# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from django.contrib.contenttypes.models import ContentType

from djanban.apps.repositories.models import GitLabRepository, Commit, GitHubPublicRepository


# Get form class for a repository
def get_form_class(repository):
    derived_type = repository.type

    # Get derived type
    if derived_type == ContentType.objects.get_for_model(GitLabRepository):
        return GitLabRepositoryForm
    elif derived_type == ContentType.objects.get_for_model(GitHubPublicRepository):
        return GitHubPublicRepositoryForm

    raise NotImplementedError(u"There is only one type of repository")


class GitLabRepositoryForm(forms.ModelForm):
    class Meta:
        model = GitLabRepository
        fields = ["name", "description", "url", "access_token", "username", "password", "project_userspace", "project_name"]

    def save(self, commit=True):
        super(GitLabRepositoryForm, self).save(commit=False)
        if commit:
            self.instance.type = ContentType.objects.get_for_model(type(self.instance))
            self.instance.save()
        return self.instance


class GitHubPublicRepositoryForm(forms.ModelForm):
    class Meta:
        model = GitHubPublicRepository
        fields = ["name", "username", "description"]

    def save(self, commit=True):
        super(GitHubPublicRepositoryForm, self).save(commit=False)
        if commit:
            if not self.instance.url:
                self.instance.url = "http://github.com/{0}/{1}".format(self.instance.username, self.instance.name)
            self.instance.type = ContentType.objects.get_for_model(type(self.instance))
            self.instance.save()
        return self.instance


# Delete repository
class DeleteRepositoryForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this repository")


# Create and edit a commit
class CommitForm(forms.ModelForm):
    class Meta:
        model = Commit
        fields = ["commit", "comments"]

    def save(self, commit=True):
        super(CommitForm, self).save(commit=False)
        if commit:
            commit_info = self.instance.repository.fetch_commit_info(self.cleaned_data["commit"])
            self.instance.creation_datetime = commit_info["creation_datetime"]
            self.instance.save()
        return self.instance


class DeleteCommitForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this commit")


class MakeAssessmentForm(forms.Form):
    LANGUAGE_CHOICES = (
        ("python", "Python"),
        ("php", "PHP"),
    )
    confirmed = forms.BooleanField(label=u"Confirm you want to make an assessment of this commit")
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)

