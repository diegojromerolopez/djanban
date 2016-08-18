# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# Warn administrators of an error
def warn_administrators(subject, message):
    email_subject = u"[DjangoTrelloStats] [Warning] {0}".format(subject)

    administrator_group = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
    administrator_users = administrator_group.user_set.all()
    for administrator_user in administrator_users:
        email_message = EmailMultiAlternatives(email_subject, message, settings.EMAIL_HOST_USER,
                                               [administrator_user.email])
        email_message.send()