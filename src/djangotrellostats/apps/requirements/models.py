from __future__ import unicode_literals

from django.db import models


# A requirement for a project
class Requirement(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="requirements")

    code = models.CharField(max_length=16, verbose_name=u"Unique code of this requirement", unique=True)

    name = models.CharField(max_length=256, verbose_name=u"Name of this requirement")

    description = models.TextField(verbose_name=u"Description of this requirement",
                                   help_text=u"Long description of this requirement describing behavior or "
                                             u"pointing to other resources.")

    cards = models.ManyToManyField("boards.Card",
                                   verbose_name=u"Tasks that depend on this requirement",
                                   related_name="requirements")

    value = models.PositiveIntegerField(verbose_name=u"Value of this requirement", default=0)

    @property
    def done_cards(self):
        return self.cards.filter(list__type="done")

    @property
    def done_cards_percentage(self):
        return  self.done_cards.count() * 100.0 / self.cards.all().count()

    @property
    def pending_cards(self):
        return self.cards.exclude(list__type="done")
