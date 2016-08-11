from __future__ import unicode_literals

import os
import sys
from io import open
import time
import traceback

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from djangotrellostats.apps.fetch.fetchers.trello import BoardFetcher, Initializer
from djangotrellostats.apps.members.models import Member


class Command(BaseCommand):
    help = u'Fetch board data'

    FETCH_LOCK_FILE_PATH = u"/tmp/django-trello-stats-fetch-lock.txt"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout=None, stderr=None, no_color=False)
        self.start_time = None
        self.end_time = None

    def add_arguments(self, parser):
        parser.add_argument('member_trello_username', nargs='+', type=str)

    def start(self):
        self.start_time = time.time()
        # Check if lock file exists. If it exists, thrown an error
        if os.path.isfile(Command.FETCH_LOCK_FILE_PATH):
            self.stdout.write(self.style.ERROR(u"Lock is in place. Unable to fetch"))
            return False

        # Creates a new lock file
        self.stdout.write(self.style.SUCCESS(u"Lock does not exist. Creating..."))
        with open(Command.FETCH_LOCK_FILE_PATH, 'w', encoding="utf-8") as lock_file:
            lock_file.write(u"Fetching data for boards")

        self.stdout.write(self.style.SUCCESS(u"Lock file created"))
        return True

    def end(self):
        self.end_time = time.time()
        # Lock file must exist
        if not os.path.isfile(Command.FETCH_LOCK_FILE_PATH):
            self.stdout.write(self.style.ERROR(u"Lock does not exist. Cancel operation"))
            return False

        # Deleting the lock file
        os.remove(Command.FETCH_LOCK_FILE_PATH)

        self.stdout.write(self.style.SUCCESS(u"Lock file deleted"))

    def elapsed_time(self):
        return self.end_time - self.start_time

    def handle(self, *args, **options):
        try:
            member_trello_username = options['member_trello_username'][0]
        except (IndexError, KeyError)as e:
            self.stdout.write(self.style.ERROR("member_username is mandatory"))
            return False

        member = Member.objects.get(trello_username=member_trello_username)
        if not member.is_initialized():
            self.stderr.write(self.style.SUCCESS(u"Member {0} is not initialized".format(member.trello_username)))
            return True

        if not self.start():
            self.stdout.write(self.style.ERROR("Unable to fetch"))
            self.warn_administrators(subject=u"Unable to fetch boards", message=u"Unable to fetch boards. Is the lock file present?")
            return False

        try:
            # Initialize boards if needed
            initializer = Initializer(member)
            initializer.init()
            self.stdout.write(self.style.SUCCESS(u"Boards initialized successfully"))

            fetch_ok = True
            last_board = None

            # For each board that is ready, fetch it
            for board in member.created_boards.filter(has_to_be_fetched=True):
                if board.is_ready():
                    last_board = board
                    self.stdout.write(self.style.SUCCESS(u"Board {0} is ready".format(board.name)))
                    board_fetcher = BoardFetcher(board)
                    board_fetcher.fetch(debug=False)
                    self.stdout.write(self.style.SUCCESS(u"Board {0} fetched successfully".format(board.name)))
                else:
                    self.stdout.write(self.style.ERROR(u"Board {0} is not ready".format(board.name)))

        # If there is any exception, warn the administrators
        except Exception as e:
            fetch_ok = False
            self.warn_administrators(subject=u"Error when fetching boards. Board {0} fetch failed".format(last_board.name),
                                     message=traceback.format_exc())
            self.stdout.write(self.style.ERROR(u"Error when fetching boards. Board {0} fetch failed".format(last_board.name)))

        # Always delete the lock file
        finally:
            self.end()

        if fetch_ok:
            self.stdout.write(self.style.SUCCESS(u"All boards fetched successfully {0}".format(self.elapsed_time())))

    # Warn administrators of an error
    def warn_administrators(self, subject, message):
        email_subject = u"[DjangoTrelloStats] [Warning] {0}".format(subject)

        administrator_group = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
        administrator_users = administrator_group.user_set.all()
        for administrator_user in administrator_users:
            email_message = EmailMultiAlternatives(email_subject, message, settings.EMAIL_HOST_USER, [administrator_user.email])
            email_message.send()
