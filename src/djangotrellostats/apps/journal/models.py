# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


# Each one of the journal entries
class JournalEntry(models.Model):

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="journal_entries")

    author = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="journal_entries")

    title = models.CharField(verbose_name=u"Title", max_length=128)

    slug = models.SlugField(verbose_name=u"Slug for this journal entry", max_length=64, unique=True)

    uuid = models.CharField(verbose_name=u"Unique uuid for short urls", max_length=16, unique=True)

    content = RichTextUploadingField(verbose_name=u"Content", help_text=u"Content of this journal entry", config_name="full")

    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    last_update_datetime = models.DateTimeField(verbose_name=u"Last update datetime")

    tags = models.ManyToManyField("journal.JournalEntryTag", verbose_name=u"Tags this entry has", blank=True)

    @property
    def ordered_tags(self):
        return self.tags.all().order_by("name")


# Each one of the tags of the journal entries
class JournalEntryTag(models.Model):
    name = models.CharField(verbose_name=u"Name", max_length=64)

    def __unicode__(self):
        return self.name