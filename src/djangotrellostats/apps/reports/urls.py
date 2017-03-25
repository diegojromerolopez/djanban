# -*- coding: utf-8 -*-

from django.conf.urls import url, include

from djangotrellostats.apps.reports.views.report_recipients import ReportRecipientListView,\
    EditReportRecipientView, CreateReportRecipientView, DeleteReportRecipientView

urlpatterns = [
    url(r'^report_recipients$', ReportRecipientListView.as_view(), name="view_report_recipient_list"),
    url(r'^report_recipients$', ReportRecipientListView.as_view(), name="view_report_recipients"),
    url(r'^report_recipients/new$', CreateReportRecipientView.as_view(), name="new_report_recipient"),
    url(r'^report_recipients/(?P<report_recipient_id>\d+)/edit$', EditReportRecipientView.as_view(), name="edit_report_recipient"),
    url(r'^report_recipients/(?P<report_recipient_id>\d+)/delete', DeleteReportRecipientView.as_view(), name="delete_report_recipient"),
]