from django.db import models


# Stat report by workflow
class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name="Name of the workflow")
    board = models.ForeignKey(
        "boards.Board",
        verbose_name="Workflow",
        related_name="workflows",
        on_delete=models.CASCADE,
    )
    lists = models.ManyToManyField(
        "boards.List", through="WorkflowList", related_name="workflow"
    )


class WorkflowList(models.Model):
    order = models.PositiveIntegerField(verbose_name="Order of the list")
    is_done_list = models.BooleanField(
        verbose_name="Informs if the list is a done list", default=False
    )
    list = models.ForeignKey(
        "boards.List",
        verbose_name="List",
        related_name="workflow_list",
        on_delete=models.CASCADE,
    )
    workflow = models.ForeignKey(
        "workflows.Workflow",
        verbose_name="Workflow",
        related_name="workflow_lists",
        on_delete=models.CASCADE,
    )


class WorkflowCardReport(models.Model):
    board = models.ForeignKey(
        "boards.Board",
        verbose_name="Board",
        related_name="workflow_card_reports",
        on_delete=models.CASCADE,
    )
    workflow = models.ForeignKey(
        "workflows.Workflow",
        verbose_name="Workflow",
        related_name="workflow_card_reports",
        on_delete=models.CASCADE,
    )
    card = models.ForeignKey(
        "boards.Card",
        verbose_name="Card",
        related_name="workflow_card_reports",
        on_delete=models.CASCADE,
    )
    lead_time = models.DecimalField(
        verbose_name="Card cycle card time",
        decimal_places=4,
        max_digits=12,
        default=None,
        null=True,
    )
    cycle_time = models.DecimalField(
        verbose_name="Card lead time",
        decimal_places=4,
        max_digits=12,
        default=None,
        null=True,
    )
