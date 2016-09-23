from __future__ import unicode_literals

from django.db import models


# Stat report by workflow
class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the workflow")
    board = models.ForeignKey("boards.Board", verbose_name=u"Workflow", related_name="workflows")
    lists = models.ManyToManyField("boards.List", through="WorkflowList", related_name="workflow")


class WorkflowList(models.Model):
    order = models.PositiveIntegerField(verbose_name=u"Order of the list")
    is_done_list = models.BooleanField(verbose_name=u"Informs if the list is a done list", default=False)
    list = models.ForeignKey("boards.List", verbose_name=u"List", related_name="workflow_list")
    workflow = models.ForeignKey("workflows.Workflow", verbose_name=u"Workflow", related_name="workflow_lists")


class WorkflowCardReport(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="workflow_card_reports")
    workflow = models.ForeignKey("workflows.Workflow", verbose_name=u"Workflow", related_name="workflow_card_reports")
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="workflow_card_reports")
    lead_time = models.DecimalField(verbose_name=u"Card cycle card time", decimal_places=4,
                                    max_digits=12, default=None, null=True)
    cycle_time = models.DecimalField(verbose_name=u"Card lead time", decimal_places=4, max_digits=12,
                                     default=None,
                                     null=True)