# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.db.models import Sum


# A requirement for a project
class Requirement(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="requirements")

    code = models.CharField(max_length=16, verbose_name=u"Unique code of this requirement", unique=True)

    name = models.CharField(max_length=256, verbose_name=u"Name of this requirement")

    description = models.TextField(verbose_name=u"Description of this requirement",
                                   help_text=u"Long description of this requirement describing behavior or "
                                             u"pointing to other resources.")

    comments = models.TextField(verbose_name=u"Comments", default="", blank=True,
                                help_text=u"Private comments for the PM and the developers")

    cards = models.ManyToManyField("boards.Card",
                                   verbose_name=u"Tasks that depend on this requirement",
                                   related_name="requirements")

    value = models.PositiveIntegerField(verbose_name=u"Value of this requirement", default=0)

    estimated_number_of_hours = models.PositiveIntegerField(verbose_name=u"Estimated number of hours to be completed",
                                                            help_text=u"Cost in hours to complete this requirement.",
                                                            blank=True, default=None, null=True)

    active = models.BooleanField(verbose_name=u"Is this requirement active?",
                                 help_text=u"Is this requirement is not active it will treat  as a wish of the client "
                                           u"but not as a real requirement",
                                 default=True)

    @property
    def done_cards(self):
        return self.cards.filter(list__type="done")

    @property
    def done_cards_percentage(self):
        num_cards = self.cards.all().count()
        if num_cards == 0:
            return 0
        return self.done_cards.count() * 100.0 / num_cards

    @property
    def done_cards_spent_time(self):
        done_cards_spent_time = self.done_cards.aggregate(sum=Sum("spent_time"))["sum"]
        if done_cards_spent_time is None:
            return 0
        return done_cards_spent_time

    @property
    def pending_cards(self):
        return self.cards.exclude(list__type="done")
