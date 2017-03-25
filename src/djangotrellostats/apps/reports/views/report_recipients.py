# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from djangotrellostats.apps.base.auth import get_user_boards, user_is_member
from djangotrellostats.apps.reports.models import ReportRecipient


# Report recipient list
class ReportRecipientListView(ListView):
    template_name = "reports/report_recipients/list.html"
    model = ReportRecipient

    def get_context_data(self, **kwargs):
        context = super(ReportRecipientListView, self).get_context_data(**kwargs)
        if user_is_member(self.request.user):
            context["member"] = self.request.user.member
        context["report_recipients"] = ReportRecipient.objects.all().order_by("email")
        context["user_boards"] = get_user_boards(self.request.user)
        context["user_boards_ids"] = {board.id: board for board in get_user_boards(self.request.user)}
        return context


# Base class for adding context to modification views for ReportRecipient objects
class ReportRecipientViewContext(object):
    def get_context_data(self, **kwargs):
        context = super(ReportRecipientViewContext, self).get_context_data(**kwargs)
        if user_is_member(self.request.user):
            context["member"] = self.request.user.member
        context["report_recipient"] = self.object
        return context


# Base class for ReportRecipient modification
class ModifyReportRecipientView(object):
    def get_form(self, *args, **kwargs):
        form = super(ModifyReportRecipientView, self).get_form(*args, **kwargs)
        boards = get_user_boards(self.request.user).order_by("name")
        form.fields['boards'].choices = [(board.id, board.name) for board in boards]
        return form


# Report recipient edition
class CreateReportRecipientView(ReportRecipientViewContext, ModifyReportRecipientView, CreateView):
    template_name = "reports/report_recipients/new.html"
    model = ReportRecipient
    fields = ("first_name", "last_name", "email", "is_active", "boards")
    success_url = reverse_lazy("reports:view_report_recipient_list")


# Edit recipient edition
class EditReportRecipientView(ReportRecipientViewContext, ModifyReportRecipientView, UpdateView):
    template_name = "reports/report_recipients/edit.html"
    model = ReportRecipient
    fields = ("first_name", "last_name", "email", "is_active", "boards")
    pk_url_kwarg = "report_recipient_id"
    success_url = reverse_lazy("reports:view_report_recipient_list")


# Delete recipient edition
class DeleteReportRecipientView(ReportRecipientViewContext, DeleteView):
    template_name = "reports/report_recipients/delete.html"
    model = ReportRecipient
    pk_url_kwarg = "report_recipient_id"
    success_url = reverse_lazy("reports:view_report_recipient_list")
