# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from djanban.apps.recurrent_cards.models import WeeklyRecurrentCard
from djanban.apps.work_hours_packages.models import WorkHoursPackage


# Notification completion email send
class Command(BaseCommand):
    help = u'Create real cards from the recurrent cards'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super(Command, self).__init__(stdout, stderr, no_color)

    # Handle de command action
    def handle(self, *args, **options):
        today = timezone.now().today()
        weekday = today.isoweekday()

        recurrent_cards_filter = {"is_active": True, "board__is_archived": False}
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

        for recurrent_card in recurrent_cards:
            card = recurrent_card.create_card()
            self.stdout.write(
                self.style.SUCCESS(
                    u"{0} successfully created".format(card.name))
            )

        self.stdout.write(
                self.style.SUCCESS(
                    u"Creation of cards from recurrent cards completed successfully")
            )