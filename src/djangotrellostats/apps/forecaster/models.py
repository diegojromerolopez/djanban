# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import shortuuid
from django.conf import settings
from django.core.files import File
from django.db import models, transaction

import statsmodels.api as sm
from django.utils import timezone

from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.serializer import CardSerializer


# Forecaster model. Provide save and load functionality used to store and retrieve regression models.
class Forecaster(models.Model):
    board = models.ForeignKey(
        "boards.Board", related_name="forecasters", verbose_name=u"Board of this forecaster",
        null=True, default=None, blank=True
    )
    member = models.ForeignKey(
        "members.Member", related_name="forecasters", verbose_name=u"Member of this forecaster",
        null=True, default=None, blank=True
    )
    name = models.CharField(verbose_name=u"Name", max_length=1024)
    model = models.CharField(verbose_name=u"Regression model", max_length=32)
    formula = models.TextField(verbose_name=u"Formula")
    summary = models.TextField(verbose_name=u"Summary", blank=True, default="")
    results_file = models.FileField(verbose_name=u"Field with the statsmodels results")
    last_update_datetime = models.DateTimeField(verbose_name=u"Last update datetime")

    # Retrieve the RegressionResults statsmodels object from database
    def get_regression_results(self):
        return sm.load(self.results_file.path)

    # Create a forecaster from a RegressionResults object
    @staticmethod
    def create_from_regressor(regressor, name=None):
        member = regressor.member
        board = regressor.board
        model = regressor.__class__.__name__
        formula = regressor.get_formula()
        results = regressor.results

        now = timezone.now()
        now_str = now.isoformat()
        tmp_path = os.path.join(settings.TMP_DIR, "{0}.pickle".format(shortuuid.uuid()))
        results.save(tmp_path)

        try:
            forecaster = Forecaster.objects.get(
                member=member, board=board, model=model, formula=formula
            )
        except Forecaster.DoesNotExist:
            forecaster = Forecaster(member=member, board=board, model=model, formula=formula)

        forecaster.name = name
        forecaster.summary = results.summary()

        with open(tmp_path, "r") as sm_results_pickle_file:
            forecaster.results_file.save(
                "{0}-{1}-{2}.pickle".format(model, now_str, shortuuid.uuid()),
                File(sm_results_pickle_file)
            )
        forecaster.save()

        return forecaster

    @property
    def test_cards(self):
        cards = Card.objects.filter(is_closed=False, spent_time__gt=0, list__type="done")
        if self.board:
            cards = cards.filter(board=self.board)
        elif self.member:
            cards = cards.filter(members=self.member)
        return cards

    # Estimate card spent time
    def estimate_spent_time(self, card):
        if not hasattr(self, "_regression_results"):
            self._regression_results = self.get_regression_results()
        return float(self._regression_results.predict([self._get_card_data(card)]))

    # Set last_update datetime when saving a Forecaster
    def save(self, *args, **kwargs):
        self.last_update_datetime = timezone.now()
        super(Forecaster, self).save(*args, **kwargs)

    # Serialize card data
    def _get_card_data(self, card):
        members = card.board.members.all()
        serializer = CardSerializer(card, members)
        return serializer.serialize()
