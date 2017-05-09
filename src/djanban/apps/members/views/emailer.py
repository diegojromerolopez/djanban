# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template


# Send email to new created member
# We send the password in plaintext, which is a bad practice but we warn the user to change as soon as possible.
def send_new_member_email(member, password):
    replacements = {"member": member, "password": password}

    txt_message = get_template('members/emails/new_member.txt').render(replacements)
    html_message = get_template('members/emails/new_member.html').render(replacements)

    subject = "Welcome to Djanban"

    return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[member.user.email],
                     fail_silently=False, html_message=html_message)