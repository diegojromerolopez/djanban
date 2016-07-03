from __future__ import unicode_literals

from django.db import models


class List(models.Model):
    LIST_TYPES = ("normal", "development", "done")
    LIST_TYPE_CHOICES = (
        ("normal", "Normal"),
        ("development", "In development"),
        ("done", "Done")
    )
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the list", unique=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="lists")
    type = models.CharField(max_length=64, choices=LIST_TYPE_CHOICES, default="normal")


class Board(models.Model):
    COMMENT_SPENT_ESTIMATED_TIME_REGEX = "PLUS_FOR_TRELLO_REGEX"

    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="boards")
    name = models.CharField(max_length=128, verbose_name=u"Name of the board")
    uuid = models.CharField(max_length=128, verbose_name=u"Trello id of the board", unique=True)
    last_activity_date = models.DateTimeField(verbose_name=u"Last activity date", default=None, null=True)


class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the workflow")
    board = models.ForeignKey("boards.Board", verbose_name=u"Workflow", related_name="workflows")
    lists = models.ManyToManyField("boards.List", through="WorkflowList", related_name="workflow")


class WorkflowList(models.Model):
    order = models.PositiveIntegerField(verbose_name=u"Order of the list")
    is_done_list = models.BooleanField(verbose_name=u"Informs if the list is a done list", default=False)
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="workflowlist")
    workflow = models.ForeignKey("boards.Workflow", verbose_name=u"Workflow", related_name="workflowlists")

