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
    board = models.ForeignKey("boards.Board", verbose_name=u"Project this commit depends on",
                               related_name="commits")
    repository = models.ForeignKey("repositories.Repository", verbose_name=u"Repository this commit depends on",
                                   related_name="commits")
    commit = models.CharField(verbose_name=u"Commit repository", max_length=64)
    comments = models.TextField(verbose_name=u"Comments about this commit", blank=True, default="")
    creation_datetime = models.DateTimeField(verbose_name=u"Datetime of this commit")
    code = models.FileField(verbose_name=u"Code for this commit")

    class Meta:
        verbose_name = "commit"
        verbose_name_plural = "commits"
        index_together = (
            ("board", "repository", "commit"),
        )

    @property
    def has_python_assessment_report(self):
        return self.pylint_messages.all().exists()

    @property
    def has_php_assessment_report(self):
        return self.phpmd_messages.all().exists()

    @property
    def has_assessment_report(self):
        return self.has_python_assessment_report or self.has_php_assessment_report


class CommitFile(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Project this linting message depends on",
                              related_name="commit_files")

    repository = models.ForeignKey("repositories.Repository",
                                   verbose_name=u"Repository this linting message depends on",
                                   related_name="commit_files")

    commit = models.ForeignKey("repositories.Commit",
                               verbose_name=u"Commit this source code file depends on",
                               related_name="files")

    language = models.CharField(verbose_name=u"Language of the file", max_length=64)

    path = models.CharField(verbose_name=u"File", max_length=512)

    blank_lines = models.PositiveIntegerField(verbose_name=u"Number of blank lines in this file")

    commented_lines = models.PositiveIntegerField(verbose_name=u"Number of commented lines")

    lines_of_code = models.PositiveIntegerField(verbose_name=u"Lines of code")

    class Meta:
        verbose_name = "commit file"
        verbose_name_plural = "commit files"
        index_together = (
            ("board", "repository", "commit", "language"),
        )

    @staticmethod
    def create_from_cloc_result(commit, cloc_result):
        repository = commit.repository
        commit_file = CommitFile(
            commit=commit, repository=repository, board=repository.board,
            language=cloc_result["language"],
            path=cloc_result["path"],
            blank_lines=cloc_result["blank_lines"],
            commented_lines=cloc_result["commented_lines"],
            lines_of_code=cloc_result["lines_of_code"],
        )
        commit_file.save()
        return commit_file


# PHP-md messages
class PhpMdMessage(models.Model):
    RULESETS = ("Clean Code Rules",
                "Code Size Rules",
                "Controversial Rules",
                "Design Rules",
                "Naming Rules",
                "Unused Code Rules")

    board = models.ForeignKey("boards.Board", verbose_name=u"Project this linting message depends on",
                              related_name="phpmd_messages")

    repository = models.ForeignKey("repositories.Repository",
                                   verbose_name=u"Repository this linting message depends on",
                                   related_name="phpmd_messages")

    commit = models.ForeignKey("repositories.Commit", verbose_name=u"Commit this linting message depends on",
                               related_name="phpmd_messages")

    commit_file = models.ForeignKey("repositories.CommitFile",
                                    verbose_name=u"Commit file this linting message depends on",
                                    related_name="phpmd_messages")

    path = models.CharField(verbose_name=u"File", max_length=512)

    message = models.TextField(verbose_name=u"Assessment message content")

    rule = models.CharField(verbose_name=u"Violated rule", max_length=64, default=None, null=True)

    ruleset = models.CharField(verbose_name=u"Rule set", max_length=64, default=None, null=True)

    begin_line = models.IntegerField(verbose_name=u"Begin line where the error happens", default=None, null=True)

    end_line = models.IntegerField(verbose_name=u"End line where the error happens", default=None, null=True)

    class Meta:
        verbose_name = u"phpmd message"
        verbose_name_plural = u"phpmd messages"
        index_together = (
            ("board", "repository", "commit", "commit_file", "ruleset"),
            ("commit", "commit_file", "ruleset"),
            ("board", "commit", "ruleset"),
            ("board", "commit", "commit_file", "ruleset"),
            ("board", "ruleset")
        )

    @staticmethod
    def create_all(commit, phpmd_results):
        repository = commit.repository
        board = commit.board
        for phpmd_result in phpmd_results:
            commit_file = CommitFile.create_from_cloc_result(commit, phpmd_result.cloc_result)
            for phpmd_result_message in phpmd_result.messages:
                phpmd_message = PhpMdMessage(board=board, repository=repository, commit=commit, commit_file=commit_file,
                                             rule=phpmd_result_message["rule"],
                                             ruleset=phpmd_result_message["ruleset"],
                                             message=phpmd_result_message["message"],
                                             path=phpmd_result_message["path"],
                                             begin_line=phpmd_result_message["begin_line"],
                                             end_line=phpmd_result_message["end_line"])
                phpmd_message.save()


# Pylint messages
class PylintMessage(models.Model):

    TYPE_CHOICES = (
        ("convention", "Coding standard violation"),
        ("error", "Standard programming error"),
        ("refactor", "Needs refactoring"),
        ("warning", "Warning")
    )

    class Meta:
        verbose_name = u"pylint message"
        verbose_name_plural = u"pylint messages"
        index_together = (
            ("board", "repository", "commit", "commit_file", "type"),
            ("commit", "type"),
            ("board", "commit", "type"),
            ("board", "type")
        )

    board = models.ForeignKey("boards.Board", verbose_name=u"Project this linting message depends on",
                              related_name="pylint_messages")

    commit = models.ForeignKey("repositories.Commit", verbose_name=u"Commit this linting message depends on",
                               related_name="pylint_messages")

    repository = models.ForeignKey("repositories.Repository", verbose_name=u"Repository this linting message depends on",
                                   related_name="pylint_messages")

    commit_file = models.ForeignKey("repositories.CommitFile",
                                    verbose_name=u"Commit file this linting message depends on",
                                    related_name="pylint_messages")

    type = models.CharField(verbose_name=u"Message type", max_length=256)

    path = models.CharField(verbose_name=u"File", max_length=512)

    message = models.TextField(verbose_name=u"Assessment message content")

    message_symbolic_name = models.CharField(verbose_name=u"Message content", max_length=64, default="", blank=True)

    line = models.IntegerField(verbose_name=u"Line where the error happens")

    column = models.IntegerField(verbose_name=u"Column where the error happens")

    object = models.CharField(verbose_name=u"Object", max_length=256)

    @staticmethod
    def create_from_dict(board, repository, commit, pylinter_result):
        commit_file = CommitFile.create_from_cloc_result(commit, pylinter_result.cloc_result)
        for pylinter_result_message in pylinter_result.messages:
            if pylinter_result_message:
                dict_message = pylinter_result_message
                linting_message = PylintMessage(
                    board=board, repository=repository, commit=commit, commit_file=commit_file,
                    path=dict_message["path"], type=dict_message["type"], message=dict_message["message"],
                    message_symbolic_name=dict_message["symbol"], line=dict_message["line"], column=dict_message["column"],
                    object=dict_message["obj"]
                )
                linting_message.save()

    @staticmethod
    def create_all(commit, pylinter_results):
        repository = commit.repository
        board = commit.board
        for pylinter_result in pylinter_results:
            PylintMessage.create_from_dict(board, repository, commit, pylinter_result)

