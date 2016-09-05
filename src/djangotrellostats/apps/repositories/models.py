# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import gitlab

from django.contrib.contenttypes.models import ContentType
from django.db import models


# Repository
class Repository(models.Model):
    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"

    # Project this repository depends on
    board = models.ForeignKey("boards.Board", verbose_name=u"Project this repository depends on",
                              related_name="repositories")

    # Name for this repository
    name = models.CharField(verbose_name=u"Name of this repository", max_length=128)

    # Description of this repository
    description = models.TextField(verbose_name=u"Description for this repository", default="", blank=True)

    # Repository URL
    url = models.URLField(verbose_name=u"Repository URL")

    # Type of this repository
    type = models.ForeignKey(ContentType, editable=False)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.real_type = self._get_type()
        super(Repository, self).save(*args, **kwargs)

    def _get_type(self):
        return ContentType.objects.get_for_model(type(self))

    @property
    def derived_object(self):
        return self.type.get_object_for_this_type(pk=self.pk)

    # Fetch the commit
    def fetch_commit(self, commit):
        derived_object = self.derived_object
        commit_info = derived_object.fetch_commit(commit)
        return commit_info


# Gitlab profile for integration of that VCS
# python-gitlab will be used (https://github.com/gpocentek/python-gitlab)
class GitLabRepository(Repository):

    class Meta:
        verbose_name = "GitLab repository"
        verbose_name_plural = "GitLab repositories"

    # Token for Django Trello Stats Integration. For example: aoiefhsLFKDJj
    access_token = models.CharField(verbose_name=u"Access token for the repository", max_length=128)
    project_name = models.CharField(verbose_name=u"Project userspace/name", max_length=128)

    def __unicode__(self):
        return "Access token: {0} and project name: {1}".format(self.access_token, self.project_name)

    # Fetch a commit
    # Returns a dict with the keys code (with a File with the code)
    # and datetime (with the date and time when that commit was created)
    def fetch_commit(self, commit):
        derived_object = self.derived_object
        gl = gitlab.Gitlab(self.url, self.access_token)
        project = gl.projects.get(self.project_name)
        commit_response = project.commits.get(commit)
        #commit_code = project.repository_archive(commit=commit)
        return {"code": None, "creation_datetime": commit_response.created_at}


# Each one of the commits fetched from the repository
class Commit(models.Model):
    repository = models.ForeignKey("repositories.Repository", verbose_name=u"Repository this commit depends on",
                                   related_name="commits")
    commit = models.CharField(verbose_name=u"Commit repository", max_length=64)
    comments = models.TextField(verbose_name=u"Comments about this commit", blank=True, default="")
    creation_datetime = models.DateTimeField(verbose_name=u"Datetime of this commit")
    code = models.FileField(verbose_name=u"Code for this commit")

