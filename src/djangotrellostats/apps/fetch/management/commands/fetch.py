from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from multiprocessing import Process

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member
import time


class Command(BaseCommand):
    help = 'Fetch board data'

    def add_arguments(self, parser):
        parser.add_argument('member_trello_username', nargs='+', type=str)

    @transaction.atomic
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
        for board in member.created_boards.all():

            def fetch_board_i():
                board.fetch()
                self.stdout.write(self.style.SUCCESS(u"Board {0} fetched successfully".format(board.name)))

            if board.is_ready():
                board_fetcher = Process(target=fetch_board_i)
                board_fetcher.start()
                board_fetcher.join()

            else:
                self.stdout.write(self.style.SUCCESS(u"Board {0} is not ready".format(board.name)))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(self.style.SUCCESS(u"All boards fetched successfully {0}".format(elapsed_time)))
