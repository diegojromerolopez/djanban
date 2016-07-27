# -*- coding: utf-8 -*-

import re
from django.forms import models
from djangotrellostats.apps.boards.models import List
from djangotrellostats.apps.workflows.models import Workflow, WorkflowList



# Workflow creation form
class NewWorkflowForm(models.ModelForm):
    class Meta:
        model = Workflow
        fields = ["name"]

    def __init__(self, workflow, *args, **kwargs):
        super(NewWorkflowForm, self).__init__(*args, **kwargs)
        self.instance = workflow
        # Creation of pair of lists of lists for development and done
        lists = workflow.board.lists.all().order_by("id")
        num_lists = lists.count()
        list_position = {lists[i].id: i+1 for i in range(0, num_lists)}
        list_choices = [("empty", "Empty")]+[(list_.id, list_.name) for list_ in lists]

        # Development lists
        for list_i in range(0, num_lists):
            development_list_name_i = "development_list_{0}".format(list_i)
            self.fields[development_list_name_i] = models.ChoiceField(choices=list_choices, initial="empty",
                                                                      label=u"'Development' list in position {0}".format(list_i))
            # In case we are editing, get default value of the select of the lists
            if workflow.workflow_lists.filter(order=list_i, is_done_list=False).exists():
                list_id_in_position_i = workflow.workflow_lists.get(order=list_i, is_done_list=False).list_id
                self.fields[development_list_name_i].initial = list_position[list_id_in_position_i]

        # Done lists
        for list_i in range(0, num_lists):
            done_list_name_i = "done_list_{0}".format(list_i)
            self.fields[done_list_name_i] = models.ChoiceField(choices=list_choices, initial="empty",
                                                               label=u"'Done' list in position {0}".format(list_i))

            if workflow.workflow_lists.filter(order=list_i, is_done_list=True).exists():
                list_id_in_position_i = workflow.workflow_lists.get(order=list_i, is_done_list=True).list_id
                self.fields[done_list_name_i].initial = list_position[list_id_in_position_i]

    def save(self, commit=True):
        workflow = super(NewWorkflowForm, self).save(commit)

        if commit:
            # Clear existing relationships
            workflow.workflow_lists.all().delete()
            for field in self.cleaned_data:
                list_match = re.match("^(development_list|done_list)_(\d)+$", field)
                if list_match and self.cleaned_data[field] != "empty":
                    list_id = self.cleaned_data[field]

                    list_match_groups = list_match.groups()

                    list_type = list_match_groups[0]
                    list_is_done_list = (list_type == "done_list")

                    list_position = list_match_groups[1]
                    list_ = List.objects.get(id=list_id)
                    workflowlist = WorkflowList(order=list_position, is_done_list=list_is_done_list,
                                                list=list_, workflow=workflow)
                    workflowlist.save()


# Workflow edition form
class EditWorkflowForm(NewWorkflowForm):
    class Meta:
        model = Workflow
        fields = ["name"]

