from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

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
        member.init_fetch()
        for board in member.boards.all():
            board.fetch()
            self.stdout.write(self.style.SUCCESS(u"Board {0} fetched successfully".format(board.name)))

        self.stdout.write(self.style.SUCCESS(u"All boards fetched successfully"))
