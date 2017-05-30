# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import time
import traceback
from datetime import datetime, timedelta
from io import open

import pytz
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djanban.apps.base.email import warn_administrators
from djanban.apps.fetch.fetchers.trello.boards import Initializer, BoardFetcher
from djanban.apps.members.models import Member


# Creates a new supermember that can access all boards, members, charts, etc.
# It can
class Command(BaseCommand):
    help = u'Create a supermember'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+', type=str, default=False)
        parser.add_argument('password', nargs='+', type=str, default=False)

    def handle(self, *args, **options):
        if 'username' not in options or not options['username'] or len(options['username']) != 1:
            self.stdout.write(self.style.ERROR("username is mandatory"))
            return False

        if 'password' not in options or not options['password'] or len(options['password'])!=1:
            self.stdout.write(self.style.ERROR("password is mandatory"))
            return False

        username = options['username'][0]
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR("This username already exists"))
            return False

        password = options['password'][0]

        try:
            with transaction.atomic():
                # Creation of user
                user = User(username=username, is_superuser=True, is_active=True)
                user.set_password(password)
                user.save()

                # Assignment of member
                member = Member(user=user)
                member.save()

                # Assignment of user to group administrators
                administrators = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
                administrators.user_set.add(user)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR("Supermember couldn't be created successfully because of exception {0}".format(e))
            )

        # Everything went well
        self.stdout.write(
            self.style.SUCCESS("Supermember with username {0} has been created successfully".format(username))
        )
