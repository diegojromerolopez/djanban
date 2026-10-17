# -*- coding: utf-8 -*-


from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djanban.apps.boards.models import Card


# Move all cards with recurrent cards to their destination list
# Use: python manage.py move_cards_from_recurrent_cards.py
class Command(BaseCommand):
    help = "Move cards from recurrent cards"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    # Handle de command action
    def handle(self, *args, **options):
        today = timezone.now().today()
        yesterday = today - timedelta(days=1)

        cards = Card.objects.filter(
            parent_recurrent_card__isnull=False, creation_datetime__date=yesterday
        ).order_by("board")

        num_moved_cards = 0
        with transaction.atomic():
            for card in cards:
                recurrent_card = card.parent_recurrent_card
                # Move cards that have not already be moved to the destination list
                if (
                    recurrent_card.move_to_list_when_day_ends
                    and card.list.id != recurrent_card.move_to_list_when_day_ends.id
                ):
                    card.move(
                        member=recurrent_card.creator,
                        destination_list=recurrent_card.move_to_list_when_day_ends,
                        destination_position="top",
                    )
                    num_moved_cards += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Board {0}: card {1} moved to {2}".format(
                                card.board,
                                card.name,
                                recurrent_card.move_to_list_when_day_ends.name,
                            )
                        )
                    )

        # If there has been at least one movement, show a message
        if num_moved_cards > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "{0} card(s) were moved to their recurrent card destination list".format(
                        num_moved_cards
                    )
                )
            )
        # Otherwise, show another "less happy" message
        else:
            self.stdout.write(self.style.SUCCESS("No cards were moved"))
