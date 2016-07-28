from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from multiprocessing import Process

from djangotrellostats.apps.members.models import Member
import time
import os
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fetch board data'

    FETCH_LOCK_FILE_PATH = "/tmp/django-trello-stats-fetch-lock.txt"

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
        lock_file = open(Command.FETCH_LOCK_FILE_PATH, 'w')
        lock_file.write("Fetching data...")
        lock_file.close()
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
            return False

        for board in member.created_boards.all():
            if board.is_ready():
                self.stdout.write(self.style.SUCCESS(u"Board {0} is ready".format(board.name)))
                board.fetch(debug=False)
            else:
                self.stdout.write(self.style.ERROR(u"Board {0} is not ready".format(board.name)))

        self.end()

        self.stdout.write(self.style.SUCCESS(u"All boards fetched successfully {0}".format(self.elapsed_time())))
