from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from multiprocessing import Process

from djangotrellostats.apps.members.models import Member
import time


class Command(BaseCommand):
    help = 'Fetch board data'

    def add_arguments(self, parser):
        parser.add_argument('member_trello_username', nargs='+', type=str)

    def handle(self, *args, **options):
        try:
            member_trello_username = options['member_trello_username'][0]
        except (IndexError, KeyError)as e:
            self.stdout.write(self.style.SUCCESS("member_username is mandatory"))
            return False

        member = Member.objects.get(trello_username=member_trello_username)
        if not member.is_initialized():
            self.stderr.write(self.style.SUCCESS(u"Member {0} is not initialized".format(member.trello_username)))
            return True

        start = time.time()
        board_fetchers = []
        for board in member.created_boards.all():

            if board.is_ready():
                board.fetch(debug=True)

            else:
                self.stdout.write(self.style.SUCCESS(u"Board {0} is not ready".format(board.name)))

        for board_fetcher in board_fetchers:
            board_fetcher.join()

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(self.style.SUCCESS(u"All boards fetched successfully {0}".format(elapsed_time)))
