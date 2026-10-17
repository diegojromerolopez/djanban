# -*- coding: utf-8 -*-

from django.urls import re_path as url

from djanban.apps.reports.views.report_recipients import (
    CreateReportRecipientView,
    DeleteReportRecipientView,
    EditReportRecipientView,
    ReportRecipientListView,
)

app_name = "reports"

urlpatterns = [
    url(
        r"^report_recipients$",
        ReportRecipientListView.as_view(),
        name="view_report_recipient_list",
    ),
    url(
        r"^report_recipients$",
        ReportRecipientListView.as_view(),
        name="view_report_recipients",
    ),
    url(
        r"^report_recipients/new$",
        CreateReportRecipientView.as_view(),
        name="new_report_recipient",
    ),
    url(
        r"^report_recipients/(?P<report_recipient_id>\d+)/edit$",
        EditReportRecipientView.as_view(),
        name="edit_report_recipient",
    ),
    url(
        r"^report_recipients/(?P<report_recipient_id>\d+)/delete",
        DeleteReportRecipientView.as_view(),
        name="delete_report_recipient",
    ),
]
