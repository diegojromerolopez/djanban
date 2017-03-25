# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from djangotrellostats.apps.reports.models import ReportRecipient


# Warn administrators of an error
def warn_administrators(subject, message):
    email_subject = u"[DjangoTrelloStats] [Warning] {0}".format(subject)
    report_recipients = ReportRecipient.objects.filter(is_active=True, send_errors=True)
    for report_recipient in report_recipients:
        email_message = EmailMultiAlternatives(email_subject, message, settings.EMAIL_HOST_USER,
                                               [report_recipient.email])
        email_message.send()