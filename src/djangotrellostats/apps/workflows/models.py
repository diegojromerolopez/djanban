from __future__ import unicode_literals

from django.db import models


# Stat report by workflow
class Workflow(models.Model):
    name = models.CharField(max_length=128, verbose_name=u"Name of the workflow")
    board = models.ForeignKey("boards.Board", verbose_name=u"Workflow", related_name="workflows")
    lists = models.ManyToManyField("boards.List", through="WorkflowList", related_name="workflow")

    # Fetch data for this workflow, creating a workflow report
    def fetch(self, cards):
        workflow_lists = self.workflow_lists.all()
        development_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                             self.workflow_lists.filter(is_done_list=False)}
        done_lists = {workflow_list.list.uuid: workflow_list.list for workflow_list in
                      self.workflow_lists.filter(is_done_list=True)}

        workflow_card_reports = []

        for card in cards:
            trello_card = card.trello_card

            lead_time = None
            cycle_time = None

            # Lead time and cycle time only should be computed when the card is done
            if not card.is_closed and trello_card.idList in done_lists:
                # Lead time in this workflow for this card
                lead_time = sum([list_stats["time"] for list_uuid, list_stats in card.stats_by_list.items()])

                # Cycle time in this workflow for this card
                cycle_time = sum(
                    [list_stats["time"] if list_uuid in development_lists else 0 for list_uuid, list_stats in
                     card.stats_by_list.items()])

                workflow_card_report = WorkflowCardReport(board=self.board, workflow=self,
                                                          card=card, cycle_time=cycle_time, lead_time=lead_time)
                workflow_card_report.save()

                workflow_card_reports.append(workflow_card_report)

        return workflow_card_reports


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