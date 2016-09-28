# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.fetch.fetchers.trello import BoardFetcher, Initializer
from djangotrellostats.apps.members.models import Member


class Command(BaseCommand):
    help = u'Fetch board data'

    CHECKOUT_LOCK_FILE_PATH = u"/tmp/django-trello-stats-checkout-repository-lock.txt"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()
        # Check if lock file exists. If it exists and has been there for less than 30 minutes, return an error code
        if os.path.isfile(Command.CHECKOUT_LOCK_FILE_PATH):
            # If the file is not old (has been there for less than 30 minutes), return an error code
            if not Command._lock_file_is_old():
                self.stdout.write(self.style.ERROR(u"Lock is in place. Unable to do checkout"))
                return False
            # Warn administrators that lock file is too old and remove it
            lock_last_modification_date_str = Command._get_lock_file_last_modification_datetime().isoformat()
            warn_administrators(
                subject=u"Lock file removed",
                message=u"Lock file was last modified on {0} and was removed".format(lock_last_modification_date_str)
            )
            os.remove(Command.CHECKOUT_LOCK_FILE_PATH)
            self.stdout.write(self.style.SUCCESS(u"Old lock created on {0} removed.".format(lock_last_modification_date_str)))

        # Creates a new lock file
        self.stdout.write(self.style.SUCCESS(u"Lock does not exist. Creating..."))
        with open(Command.CHECKOUT_LOCK_FILE_PATH, 'w', encoding="utf-8") as lock_file:
            lock_file.write(u"Fetching data for boards")

        self.stdout.write(self.style.SUCCESS(u"Lock file created"))
        return True

    # We consider a lock file is old when has been there 2 hours or more
    @staticmethod
    def _lock_file_is_old():
        lock_file_modification_datetime = Command._get_lock_file_last_modification_datetime()
        return lock_file_modification_datetime > timezone.now() - timedelta(hours=2)

    # Gets last modification datetime of the lock file
    @staticmethod
    def _get_lock_file_last_modification_datetime():
        t = os.path.getmtime(Command.CHECKOUT_LOCK_FILE_PATH)
        local_timezone = pytz.timezone(settings.TIME_ZONE)
        return local_timezone.localize(datetime.fromtimestamp(t))

    def end(self):
        self.end_time = time.time()
        # Lock file must exist
        if not os.path.isfile(Command.CHECKOUT_LOCK_FILE_PATH):
            self.stdout.write(self.style.ERROR(u"Lock does not exist. Cancel operation"))
            return False

        # Deleting the lock file
        os.remove(Command.CHECKOUT_LOCK_FILE_PATH)

        self.stdout.write(self.style.SUCCESS(u"Lock file deleted"))

    def elapsed_time(self):
        return self.end_time - self.start_time

    def handle(self, *args, **options):

        if not self.start():
            self.stdout.write(self.style.ERROR("Unable to fetch"))
            error_message = u"Unable to do checkout. Is the lock file present?"
            warn_administrators(subject=u"Unable to do checkout", message=error_message)
            raise AssertionError(error_message)

        checkout_ok = False

        try:
            boards = Board.objects.filter(has_to_be_fetched=True).exclude(last_fetch_datetime=None)
            self.stdout.write(self.style.SUCCESS(u"You have {0} projects that could have repositories".format(
                boards.count()
            )))
            for board in boards:
                repositories = board.repositories.all()
                self.stdout.write(self.style.SUCCESS(u"There are {0} repositories of code {1}".format(
                    repositories.count(), board.name
                )))
                for repository in repositories:
                    self.stdout.write(self.style.SUCCESS(u"Repository {0}".format(repository.name)))
                    repository.checkout()
                    commits = repository.commits.filter(has_been_assessed=False)
                    self.stdout.write(
                        self.style.SUCCESS(
                            u"Repository {0} is checked out successfully and has {1} commits:".format(
                                repository.name, commits.count()
                            )
                        )
                    )
                    for commit in commits:
                        commit.assess_code_quality()
                        self.stdout.write(self.style.SUCCESS(u"- Commit {0}".format(commit.commit)))
                        self.stdout.write(self.style.SUCCESS(u"  - PHPMD Messages {0}".format(commit.phpmd_messages.count())))
                        self.stdout.write(self.style.SUCCESS(u"  - Pylint Messages {0}".format(commit.pylint_messages.count())))

                    self.stdout.write(self.style.SUCCESS(u"Repository {0} {1} commits assessed succesfully".format(
                        repository.name, commits.count()))
                    )

            checkout_ok = True

        # If after two retries the exception persists, warn the administrators
        except Exception as e:
            checkout_ok = False
            exception_message = u"We tried checkout out the code repositories but it didn't work out. {0}".format(
                    traceback.format_exc()
            )
            warn_administrators(
                subject=u"Unable to checkout repositories code",
                message=exception_message
            )
            print(exception_message)
        # Always delete the lock file
        finally:
            self.end()

        if checkout_ok:
            self.stdout.write(self.style.SUCCESS(u"All code repositories checkout out successfully {0}".format(self.elapsed_time())))

