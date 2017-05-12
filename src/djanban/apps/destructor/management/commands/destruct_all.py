# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import hashlib
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from djanban.apps.boards.models import Board
from djanban.apps.charts.models import CachedChart
from djanban.apps.dev_environment.models import Interruption, NoiseMeasurement
from djanban.apps.forecasters.models import Forecaster
from djanban.apps.hourly_rates.models import HourlyRate
from djanban.apps.journal.models import JournalEntryTag
from djanban.apps.members.models import Member, TrelloMemberProfile
from djanban.apps.multiboards.models import Multiboard
from djanban.apps.reporter.models import MotivationalVideo
from djanban.apps.reports.models import ReportRecipient


class Command(BaseCommand):
    help = 'Destruct the database and media files of this installation of Djanban'

    def add_arguments(self, parser):
        parser.add_argument('password', nargs='+', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            password = options['password'][0]
        except (IndexError, KeyError)as e:
            self.stdout.write(self.style.ERROR("password is mandatory"))
            return False

        # Checking if this installation allows destruction
        if not hasattr(settings, "DESTRUCTION_PASSWORD_CHECKSUM") or settings.DESTRUCTION_PASSWORD_CHECKSUM is None:
            self.stdout.write(self.style.ERROR("This installation does not allow destruction"))
            return False

        # Destruction of database only available if password matches the destruction password
        if hashlib.sha256(password).hexdigest() != settings.DESTRUCTION_PASSWORD_CHECKSUM:
            self.stdout.write(self.style.ERROR("Password is not correct, aborting destruction"))
            return False

        self.stdout.write(self.style.SUCCESS("Password is correct, starting destruction"))

        # Destruction of database
        Board.objects.all().delete()
        User.objects.all().delete()
        Member.objects.all().delete()
        CachedChart.objects.all().delete()
        Interruption.objects.all().delete()
        NoiseMeasurement.objects.all().delete()
        Forecaster.objects.all().delete()
        HourlyRate.objects.all().delete()
        JournalEntryTag.objects.all().delete()
        TrelloMemberProfile.objects.all().delete()
        Multiboard.objects.all().delete()
        MotivationalVideo.objects.all().delete()
        ReportRecipient.objects.all().delete()

        # Delete all media files
        # Delete media root directory
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        # Create again the media root
        os.mkdir(settings.MEDIA_ROOT)

        self.stdout.write(self.style.SUCCESS(u"Database and media files have been destructed successfully"))
