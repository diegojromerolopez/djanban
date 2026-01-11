from django.core.management.base import BaseCommand
from django.db import transaction

from djanban.apps.anonymizer.anonymizer import Anonymizer


class Command(BaseCommand):
    help = 'Anonymize all data'

    @transaction.atomic
    def handle(self, *args, **options):

        anonymizer = Anonymizer()
        fileoutput = anonymizer.run()

        self.stdout.write(self.style.SUCCESS(f"Database anonymized successfully. Output stored in file {fileoutput}"))
