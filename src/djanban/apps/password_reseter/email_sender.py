# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from django.urls import reverse


def send_password_request_link(password_request, user):
    current_request = CrequestMiddleware.get_request()
    absolute_reset_password_url = current_request.build_absolute_uri(
        reverse('password_reseter:reset_password', args=(password_request.uuid,))
    )
    replacements = {"user": user, "absolute_reset_password_url": absolute_reset_password_url}

    txt_message = get_template('password_reseter/emails/request_password_reset.txt').render(replacements)
    html_message = get_template('password_reseter/emails/request_password_reset.html').render(replacements)

    subject = "Djanban :: Request password reset"

    return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[user.email],
                     fail_silently=False, html_message=html_message)


# The password has been reset successfully
def send_password_reset_successfully_email(user):
    replacements = {"user": user}

    txt_message = get_template('password_reseter/emails/password_reset_successfully.txt').render(replacements)
    html_message = get_template('password_reseter/emails/password_reset_successfully.html').render(replacements)

    subject = "Djanban :: Password reset successfully"

    return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[user.email],
                     fail_silently=False, html_message=html_message)
