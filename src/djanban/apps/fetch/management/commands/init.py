
from __future__ import unicode_literals, absolute_import

from django.core.management.base import BaseCommand
from django.db import transaction

from djanban.apps.fetch.fetchers.trello.boards import Initializer
from djanban.apps.members.models import Member


class Command(BaseCommand):
    help = 'Initialize all boards'

    def add_arguments(self, parser):
        parser.add_argument('member_external_username', nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            member_external_username = options['member_external_username'][0]
        except (IndexError, KeyError)as e:
            self.stdout.write(self.style.SUCCESS("member_username is mandatory"))
            return False

        member = Member.objects.get(trello_member_profile__username=member_external_username)

        initializer = Initializer(member)
        initializer.init()

        self.stdout.write(self.style.SUCCESS(u"Member {0} successfully initialized".format(member.external_username)))
