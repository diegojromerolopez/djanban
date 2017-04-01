# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from djangotrellostats.apps.boards.models import Card
import numpy


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class
class LinearRegressor(object):

    def __init__(self, cards):
        self.coefficients = []
        self.cards = cards\
            .filter(is_closed=False, spent_time__gt=0, list__type="done")
        if not self.cards.exists():
            raise AssertionError(u"There are no cards")

    def run(self):
        y = [float(card.spent_time) for card in self.cards]
        x = []
        for card in self.cards:
            x.append(LinearRegressor._get_x(card))

        self.coefficients = numpy.linalg.lstsq(x, y)[0]

    def estimate_spent_time(self, card):
        x = LinearRegressor._get_x(card)
        return numpy.dot(x, self.coefficients)

    @staticmethod
    def _get_x(card):
        return [
            card.age.seconds/3600.0, card.number_of_backward_movements,
            card.number_of_comments, card.blocking_cards.count(),
            float(card.value) if card.value else 0.0, len(card.name), len(card.description),
            card.members.count(), card.labels.count()
        ]