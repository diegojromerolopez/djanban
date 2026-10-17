from django.core.management.base import BaseCommand
from django.db import transaction

from djanban.apps.members.models import Member


class Command(BaseCommand):
    help = "Initialize all boards"

    def add_arguments(self, parser):
        parser.add_argument("member_trello_username", nargs="+", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            member_trello_username = options["member_trello_username"][0]
        except (IndexError, KeyError):
            self.stdout.write(self.style.SUCCESS("member_username is mandatory"))
            return False

        member = Member.objects.get(
            trello_member_profile__username=member_trello_username
        )
        member.init_fetch(debug=True)

        self.stdout.write(
            self.style.SUCCESS(
                "Member {0} successfully initialized".format(member.external_username)
            )
        )
