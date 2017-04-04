# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import shortuuid
from django.conf import settings
from django.core.files import File
from django.db import models, transaction

import statsmodels.api as sm
from django.utils import timezone

from djangotrellostats.apps.forecaster.serializer import CardSerializer


class Forecaster(models.Model):
    board = models.ForeignKey(
        "boards.Board", related_name="forecasters", verbose_name=u"Board of this forecaster",
        null=True, default=None, blank=True
    )
    model = models.CharField(verbose_name=u"Regression model", max_length=32)
    formula = models.TextField(verbose_name=u"Formula")
    results_file = models.FileField(verbose_name=u"Field with the statsmodels results")

    def get_regression_results(self):
        return sm.load(self.results_file.path)

    @staticmethod
    def create_from_regression_results(board, model, formula, results):
        now = timezone.now()
        now_str = now.isoformat()
        tmp_path = os.path.join(settings.TMP_DIR, "{0}.pickle".format(shortuuid.uuid()))
        results.save(tmp_path)

        try:
            forecaster_regression_results = Forecaster.objects.get(
                board=board, model=model, formula=formula
            )
        except Forecaster.DoesNotExist:
            forecaster_regression_results = Forecaster(board=board, model=model, formula=formula)

        with open(tmp_path, "r") as sm_results_pickle_file:
            forecaster_regression_results.results_file.save(
                "{0}-{1}-{2}.pickle".format(model, now_str, shortuuid.uuid()),
                File(sm_results_pickle_file)
            )
        forecaster_regression_results.save()

        return forecaster_regression_results

    # Estimate card spent time
    def estimate_spent_time(self, card):
        regression_results = self.get_regression_results()
        return float(regression_results.predict([self._get_card_data(card)]))

    def _get_card_data(self, card):
        if self.board:
            members = self.board.members.all()
        else:
            members = card.members.all()
        serializer = CardSerializer(card, members)
        return serializer.serialize()
