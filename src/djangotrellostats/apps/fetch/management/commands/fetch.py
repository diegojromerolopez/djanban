# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os
import time
import traceback
from datetime import datetime, timedelta
from io import open

import pytz
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from djangotrellostats.apps.base.email import warn_administrators
from djangotrellostats.apps.fetch.fetchers.trello.boards import Initializer, BoardFetcher
from djangotrellostats.apps.members.models import Member


class Command(BaseCommand):
    help = u'Fetch board data'

    FETCH_LOCK_FILE_PATH = u"/tmp/django-trello-stats-fetch-lock.txt"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)
        self.members = []
        self.start_time = None
        self.end_time = None

    def add_arguments(self, parser):
        parser.add_argument('member_trello_username', nargs='*', type=str, default=False)

    def start(self):
        self.start_time = time.time()
        # Check if lock file exists. If it exists and has been there for less than 30 minutes, return an error code
        if os.path.isfile(Command.FETCH_LOCK_FILE_PATH):
            # If the file is not old (has been there for less than 30 minutes), return an error code
            if not Command._lock_file_is_old():
                self.stdout.write(self.style.ERROR(u"Lock is in place. Unable to fetch"))
                return False
            # Warn administrators that lock file is too old and remove it
            lock_last_modification_date_str = Command._get_lock_file_last_modification_datetime().isoformat()
            warn_administrators(
                subject=u"Lock file removed",
                message=u"Lock file was last modified on {0} and was removed".format(lock_last_modification_date_str)
            )
            os.remove(Command.FETCH_LOCK_FILE_PATH)
            self.stdout.write(self.style.SUCCESS(u"Old lock created on {0} removed.".format(lock_last_modification_date_str)))

        # Creates a new lock file
        self.stdout.write(self.style.SUCCESS(u"Lock does not exist. Creating..."))
        with open(Command.FETCH_LOCK_FILE_PATH, 'w', encoding="utf-8") as lock_file:
            lock_file.write(u"Fetching data for boards")

        self.stdout.write(self.style.SUCCESS(u"Lock file created"))
        return True

    # We consider a lock file is old when has been there 30 minutes or more
    @staticmethod
    def _lock_file_is_old():
        lock_file_modification_datetime = Command._get_lock_file_last_modification_datetime()
        return lock_file_modification_datetime > timezone.now() - timedelta(minutes=30)

    # Gets last modification datetime of the lock file
    @staticmethod
    def _get_lock_file_last_modification_datetime():
        t = os.path.getmtime(Command.FETCH_LOCK_FILE_PATH)
        local_timezone = pytz.timezone(settings.TIME_ZONE)
        return local_timezone.localize(datetime.fromtimestamp(t))

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

        if options['member_external_username']:
            try:
                member_trello_username = options['member_external_username'][0]
            except (IndexError, KeyError)as e:
                self.stdout.write(self.style.ERROR("member_username is mandatory"))
                raise AssertionError("member_username is mandatory")

            self.members = Member.objects.filter(trello_member_profile__username=member_trello_username)
        else:
            self.members = Member.objects.all()

        if not self.start():
            self.stdout.write(self.style.ERROR("Unable to fetch"))
            error_message = u"Unable to fetch boards. Is the lock file present?"
            warn_administrators(subject=u"Unable to fetch boards",
                                     message=error_message)
            raise AssertionError(error_message)

        fetch_ok = True

        # Make two retries to the fetch procsess
        for member in self.members:
            if member.is_initialized:
                self.stdout.write(
                    self.style.SUCCESS(u"# Fetching {0} boards".format(member.external_username))
                )
                try:
                    self.fetch_member_boards(member)
                    member.fetch_ok = True
                    self.stdout.write(
                        self.style.SUCCESS(u"All boards of {0} fetched successfully".format(member.external_username))
                    )
                # If after two retries the exception persists, warn the administrators
                except Exception as e:
                    fetch_ok = True
                    member.fetch_ok = False
                    traceback_stack = traceback.format_exc()
                    warn_administrators(
                        subject=u"Unable to fetch boards",
                        message=u"We tried initializing the boards but it didn't work out. {0}".format(traceback_stack)
                    )

        self.end()

        if fetch_ok:
            self.stdout.write(self.style.SUCCESS(u"All boards of {0} members fetched successfully {1}".format(
                self.members.count(), self.elapsed_time()))
            )

    # Fetch boards
    def fetch_member_boards(self, member):
        last_board = None
        try:
            # For each board that is ready, fetch it
            for board in member.created_boards.filter(has_to_be_fetched=True, is_archived=False):
                if board.is_ready():
                    last_board = board
                    self.stdout.write(self.style.SUCCESS(u"Board {0} is ready".format(board.name)))
                    self.fetch_board(member, board)
                    self.stdout.write(self.style.SUCCESS(u"Board {0} fetched successfully".format(board.name)))
                else:
                    self.stdout.write(self.style.ERROR(u"Board {0} is not ready".format(board.name)))

        # If there is any exception, warn the administrators
        except Exception as e:
            if last_board:
                error_message = u"Error when fetching boards. Board {0} fetch failed.".format(last_board.name)
                initializer = Initializer(member, debug=False)
                initializer.init(last_board.uuid)
            else:
                error_message = u"Error when fetching boards."
            # Warn the administrators messaging them the traceback and show the error on stdout
            warn_administrators(subject=error_message, message=traceback.format_exc())
            self.stdout.write(self.style.ERROR(error_message))

    # Fetch one board
    def fetch_board(self, member, board):
        num_retries = 0
        while num_retries < 2:
            try:
                num_retries += 1
                board_fetcher = BoardFetcher(board)
                board_fetcher.fetch(debug=False)
            except Exception as e:
                if num_retries < 2:
                    # Initialize board if needed
                    initializer = Initializer(member, debug=False)
                    initializer.init(board.uuid)
                else:
                    raise e

