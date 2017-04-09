# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import shortuuid
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.core.files import File
from django.db import models, transaction

import statsmodels.api as sm
from django.db.models import Q
from django.utils import timezone

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecasters.serializer import CardSerializer
from djangotrellostats.apps.members.models import Member


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
    creator = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="created_forecasters")
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

        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        if not hasattr(current_user, "member"):
            raise ValueError("User needs to be member to create a forecaster")
        current_member = current_user.member

        forecaster.creator = current_member
        forecaster.name = name
        forecaster.summary = results.summary()

        with open(tmp_path, "r") as sm_results_pickle_file:
            forecaster.results_file.save(
                "{0}-{1}-{2}.pickle".format(model, now_str, shortuuid.uuid()),
                File(sm_results_pickle_file)
            )
        forecaster.save()

        # Delete all current forecasts (if we were updating the forecaster)
        forecaster.forecasts.all().delete()

        return forecaster

    @property
    def test_cards(self):
        cards = Card.objects.filter(is_closed=False, spent_time__gt=0, list__type="done")
        if self.board:
            cards = cards.filter(board=self.board)
        elif self.member:
            cards = cards.filter(members=self.member)
        return cards

    # Make an estimation of a card
    # Returns the estimated spent time of this card according to this forecaster's model
    def estimate_spent_time(self, card):
        if not hasattr(self, "_regression_results"):
            self._regression_results = self.get_regression_results()
        estimate_spent_time = float(self._regression_results.predict([self._get_card_data(card)]))
        return estimate_spent_time

    # Make a forecast of a card
    # Returns a Forecast object with the estimated spent time of this card according to this forecaster's model
    def make_forecast(self, card):

        # If Forecast object exists, return it
        try:
            return Forecast.objects.get(forecaster=self, card=card, last_update_datetime__gte=self.last_update_datetime)
        # Otherwise,
        except Forecast.DoesNotExist:
            # Try getting an old forecast and updating it if it exists
            try:
                forecast = Forecast.objects.get(forecaster=self, card=card)
            # If it doesn't exist, create a new one
            except Forecast.DoesNotExist:
                forecast = Forecast(forecaster=self, card=card)

            forecast.last_update_datetime = timezone.now()
            forecast.estimated_spent_time = self.estimate_spent_time(card)
            forecast.save()
        return forecast

    # Set last_update datetime when saving a Forecaster
    def save(self, *args, **kwargs):
        self.last_update_datetime = timezone.now()
        super(Forecaster, self).save(*args, **kwargs)

    # Get all forecasters accessible for a particular member of this application
    @staticmethod
    def get_all_from_member(member):
        user = member.user
        boards = get_user_boards(user)
        teammates = Member.get_user_team_mates(user)
        forecasters = Forecaster.objects.filter(
            Q(creator=member) |
            Q(board__in=boards) |
            Q(member__in=list(teammates)+[member])
        )
        return forecasters

    # Serialize card data
    def _get_card_data(self, card):
        members = card.board.members.all()
        serializer = CardSerializer(card, members)
        return serializer.serialize()


# Estimation of spent time for a card
class Forecast(models.Model):
    class Meta:
        unique_together = (
            ("forecaster", "card")
        )

    forecaster = models.ForeignKey(
        "forecasters.Forecaster", related_name="forecasts",
        verbose_name=u"Spent time for this forecast"
    )
    card = models.ForeignKey("boards.Card", related_name="forecasts", verbose_name=u"Card for this forecast")
    estimated_spent_time = models.DecimalField(verbose_name=u"Estimated spent time", decimal_places=4, max_digits=12)
    last_update_datetime = models.DateTimeField(verbose_name=u"Date this estimation was done")
