# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shortuuid
from datetime import timedelta
from django.db import models


# Each one of the password reset request
from django.utils import timezone

from djanban.apps.password_reseter.email_sender import send_password_request_link, \
    send_password_reset_successfully_email


class PasswordResetRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
    )
    # User this password request belongs to
    user = models.ForeignKey("auth.User", verbose_name=u"User", related_name="password_reset_requests")

    # Unique identifier
    uuid = models.CharField(verbose_name=u"Uuid", max_length=64, unique=True)

    # Creation datetime
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    # Maximum date this password reset request will be managed
    limit_datetime = models.DateTimeField(verbose_name=u"Maximum life datetime")

    # Date where this password reset request has been accomplished
    completion_datetime = models.DateTimeField(verbose_name=u"Completion datetime", null=True, default=None, blank=True)

    status = models.CharField(verbose_name=u"Status of this request",
                              max_length=16, choices=STATUS_CHOICES, default="pending")

    @staticmethod
    def user_has_a_pending_new_password_request(user):
        now = timezone.now()
        exitst_other_requests = user.password_reset_requests.filter(
            status="pending", completion_datetime__isnull=True, limit_datetime__gt=now
        ).exists()
        return exitst_other_requests

    @staticmethod
    def request_new_password(user, send_email=True):
        # Creation of model object
        uuid = shortuuid.ShortUUID().random(length=32).lower()
        creation_datetime = timezone.now()
        limit_datetime = creation_datetime + timedelta(days=1)
        password_reset_request = PasswordResetRequest(
            user=user, uuid=uuid, creation_datetime=creation_datetime, limit_datetime=limit_datetime
        )
        password_reset_request.save()

        # Send email with reset password link
        if send_email:
            send_password_request_link(password_reset_request, user)

        return password_reset_request

    def set_password(self, password, send_email=True):
        # Setting password
        user = self.user
        user.set_password(password)
        user.save()
        # Mark this password reset request as done
        self.status = "completed"
        self.completion_datetime = timezone.now()
        self.save()
        # Send email confirming password reset
        if send_email:
            send_password_reset_successfully_email(user);