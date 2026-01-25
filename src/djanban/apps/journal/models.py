# -*- coding: utf-8 -*-


from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models


# Each one of the journal entries
class JournalEntry(models.Model):

    board = models.ForeignKey(
        "boards.Board",
        verbose_name="Board",
        related_name="journal_entries",
        on_delete=models.CASCADE,
    )

    author = models.ForeignKey(
        "members.Member",
        verbose_name="Member",
        related_name="journal_entries",
        on_delete=models.CASCADE,
    )

    title = models.CharField(verbose_name="Title", max_length=128)

    slug = models.SlugField(
        verbose_name="Slug for this journal entry", max_length=64, unique=True
    )

    uuid = models.CharField(
        verbose_name="Unique uuid for short urls", max_length=16, unique=True
    )

    content = RichTextUploadingField(
        verbose_name="Content",
        help_text="Content of this journal entry",
        config_name="full",
    )

    creation_datetime = models.DateTimeField(verbose_name="Creation datetime")

    last_update_datetime = models.DateTimeField(verbose_name="Last update datetime")

    tags = models.ManyToManyField(
        "journal.JournalEntryTag", verbose_name="Tags this entry has", blank=True
    )

    @property
    def ordered_tags(self):
        return self.tags.all().order_by("name")


# Each one of the tags of the journal entries
class JournalEntryTag(models.Model):
    name = models.CharField(verbose_name="Name", max_length=64)

    def __str__(self):
        return self.name
