# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import subprocess

import gitlab
import os

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone

from djangotrellostats.apps.repositories.phpmd import PhpDirectoryAnalyzer
from djangotrellostats.apps.repositories.pylinter import PythonDirectoryAnalyzer


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

    def checkout(self, commit=None):
        derived_object = self.derived_object
        return derived_object.checkout(commit)

    @property
    def repository_path(self):
        return self.derived_object.repository_path

    # Fetch the commit
    def fetch_commit(self, commit):
        derived_object = self.derived_object
        commit_info = derived_object.fetch_commit(commit)
        return commit_info

    # Has this repository assessed Python code?
    @property
    def has_python_assessment_report(self):
        return self.pylint_messages.all().exists()

    # Has this repository assessed PHP code?
    @property
    def has_php_assessment_report(self):
        return self.phpmd_messages.all().exists()


# Gitlab profile for integration of that VCS
# python-gitlab will be used (https://github.com/gpocentek/python-gitlab)
class GitLabRepository(Repository):

    class Meta:
        verbose_name = "GitLab repository"
        verbose_name_plural = "GitLab repositories"

    # Token for Django Trello Stats Integration. For example: aoiefhsLFKDJj
    access_token = models.CharField(verbose_name=u"Access token for the repository", max_length=128)

    # CI token
    ci_token = models.CharField(verbose_name=u"CI token for the repository",
                                help_text=u"CI token used to clone and checkout the repository",
                                max_length=128)

    # Userspace of repository full name (userspace/name)
    project_userspace = models.CharField(verbose_name=u"Project userspace", max_length=128)

    # Name of repository full name (userspace/name)
    project_name = models.CharField(verbose_name=u"Project name", max_length=128)

    def __unicode__(self):
        return "Access token: {0} and project name: {1}".format(self.access_token, self.project_name)

    @property
    def project_full_name(self):
        return u"{0}/{1}".format(self.project_userspace, self.project_name)

    @property
    def repository_path(self):
        return u"{0}{1}/{2}".format(settings.TMP_DIR, self.project_userspace, self.project_name)

    @property
    def userspace_path(self):
        return u"{0}{1}".format(settings.TMP_DIR, self.project_userspace)

    # Delete the repository
    def delete(self):
        with transaction.atomic():
            os.removedirs(self.repository_path)
            super(GitLabRepository, self).delete()

    # Checkout a repository
    def checkout(self, commit=None):

        # Create userspace directory if needed
        repository_userspace = self.userspace_path
        if not os.path.exists(repository_userspace):
            os.makedirs(repository_userspace)

        # Create directory inside userspace if needed
        repository_dir = self.repository_path
        if not os.path.exists(repository_dir):
            clone_command = "git clone https://gitlab-ci-token:{0}@{1}/{2}/{3}.git {4}".format(
                self.ci_token, self.url.replace("http://", ""), self.project_userspace, self.project_name, repository_dir
            )

            print clone_command
            clone_result = subprocess.Popen(clone_command, shell=True, stdout=subprocess.PIPE)
            clone_stdout = clone_result.stdout.read()
            print clone_stdout

        # Pull all changes
        pull_command = "cd {0} && git fetch --all && cd -".format(repository_dir)
        print pull_command
        pull_result = subprocess.Popen(pull_command, shell=True, stdout=subprocess.PIPE)
        pull_stdout = pull_result.stdout.read()
        print pull_stdout

        if commit:
            checkout_command = "cd {0} && git checkout {1} && cd -".format(repository_dir, commit)
            print checkout_command
            checkout_result = subprocess.Popen(checkout_command, shell=True, stdout=subprocess.PIPE)
            checkout_stdout = checkout_result.stdout.read()
            print checkout_stdout

    # Fetch a commit
    # Returns a dict with the keys code (with a File with the code)
    # and datetime (with the date and time when that commit was created)
    def fetch_commit(self, commit):
        # Get commit info
        gl = gitlab.Gitlab(self.url, self.access_token)
        project = gl.projects.get(self.project_full_name)
        commit_response = project.commits.get(commit)
        # Checkout commit
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

    has_been_assessed = models.BooleanField(verbose_name=u"Informs if the commit code has been assessed", default=False)

    assessment_datetime = models.DateTimeField(verbose_name=u"Assessment date and time", default=None, null=True)

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

    def checkout(self):
        repository = self.repository
        repository.checkout(self.commit)

    @transaction.atomic
    def assess_code_quality(self):
        # Deletion of current commit files and Pylint and PHP-md messages
        self.files.all().delete()
        self.phpmd_messages.all().delete()
        self.pylint_messages.all().delete()

        # Checkout of this commit
        self.checkout()

        project_file_path = self.repository.repository_path

        # Analysis of the PHP code in the repository
        dir_phpmd_analyzer = PhpDirectoryAnalyzer(project_file_path)
        results = dir_phpmd_analyzer.run()
        PhpMdMessage.create_all(self, results)

        # Analysis of the Python code in the repository
        dir_pylinter = PythonDirectoryAnalyzer(project_file_path)
        pylinter_results = dir_pylinter.run()
        PylintMessage.create_all(self, pylinter_results)

        # Mark the commit as already assessed
        self.has_been_assessed = True
        self.assessment_datetime = timezone.now()
        self.save()


# Each one of the files of this commit
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

