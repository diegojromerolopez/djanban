# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djanban.apps.recurrent_cards.models import WeeklyRecurrentCard


# Notification completion email send
class Command(BaseCommand):
    help = u'Create real cards from the recurrent cards'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    # Handle de command action
    def handle(self, *args, **options):
        today = timezone.now().today()
        weekday = today.isoweekday()

        recurrent_cards_filter = {
            "is_active": True,
            "board__is_archived": False
        }
        if weekday == 1:
            recurrent_cards_filter["create_on_mondays"] = True
        elif weekday == 2:
            recurrent_cards_filter["create_on_tuesdays"] = True
        elif weekday == 3:
            recurrent_cards_filter["create_on_wednesdays"] = True
        elif weekday == 4:
            recurrent_cards_filter["create_on_thursdays"] = True
        elif weekday == 5:
            recurrent_cards_filter["create_on_fridays"] = True
        elif weekday == 6:
            recurrent_cards_filter["create_on_saturdays"] = True
        elif weekday == 7:
            recurrent_cards_filter["create_on_sundays"] = True

        recurrent_cards = WeeklyRecurrentCard.objects.filter(**recurrent_cards_filter)

        num_created_cards = 0

        with transaction.atomic():
            for recurrent_card in recurrent_cards:
                # Check if has already created a card today
                has_created_a_card_today = recurrent_card.has_created_a_card_today
                # In case a card has not been already created today for this recurrent card,
                # create it (also in its backend)
                if not has_created_a_card_today:
                    card = recurrent_card.create_card()
                    num_created_cards += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            u"{0} successfully created".format(card.name))
                    )
                # In case a card has been already created for this recurrent card, show a warning
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            u"card {0} already created today".format(recurrent_card.name))
                    )

        # If there has been at least one creation of card, show a message
        if num_created_cards > 0:
            self.stdout.write(
                    self.style.SUCCESS(
                        u"Creation of {0} card(s) from recurrent cards completed successfully".format(num_created_cards)
                    )
                )
        # Otherwise, show another "less happy" message
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    u"No recurrent cards for this day, hence, no cards were created"
                )
            )