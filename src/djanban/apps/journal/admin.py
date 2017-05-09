from django.contrib import admin

from djanban.apps.journal.models import JournalEntry

admin.site.register(JournalEntry)
