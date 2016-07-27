from django.contrib import admin

# Register your models here.
from djangotrellostats.apps.workflows.models import Workflow, WorkflowList

admin.site.register(Workflow)
admin.site.register(WorkflowList)