from django.urls import path, re_path

from djanban.apps.reports.views.report_recipients import ReportRecipientListView,\
    EditReportRecipientView, CreateReportRecipientView, DeleteReportRecipientView


app_name = 'reports'

urlpatterns = [
    path('report_recipients', ReportRecipientListView.as_view(), name="view_report_recipient_list"),
    path('report_recipients', ReportRecipientListView.as_view(), name="view_report_recipients"),
    path('report_recipients/new', CreateReportRecipientView.as_view(), name="new_report_recipient"),
    path('report_recipients/<int:report_recipient_id>/edit', EditReportRecipientView.as_view(), name="edit_report_recipient"),
    re_path(r'^report_recipients/(?P<report_recipient_id>\d+)/delete', DeleteReportRecipientView.as_view(), name="delete_report_recipient"),
]