# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from djangotrellostats.apps.boards.models import Card, List

import pandas as pd
import statsmodels.formula.api as sm


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class
class Regressor(object):

    def __init__(self, cards, members=None):
        self.result = None
        self.cards = cards\
            .filter(is_closed=False, spent_time__gt=0, list__type="done")
        if members:
            self.members = members
        else:
            self.members = []
        if not self.cards.exists():
            raise AssertionError(u"There are no cards")

    def run(self):
        df = self._get_data_frame()
        formula = "card_spent_time ~ card_age + num_forward_movements + num_backward_movements + num_comments + length_name + length_description + num_members"
        for member in self.members:
            formula += " + {0}".format(member.external_username)
        for list_type in List.LIST_TYPES:
            formula += " + creation_list_type_{0}".format(list_type)
        self.result = sm.ols(formula=formula, data=df).fit()

    def estimate_spent_time(self, card):
        return self.result.predict([self._get_card_data(card)])

    def _get_data_frame(self):
        data_dict = [self._get_card_data(card) for card in self.cards]
        df = pd.DataFrame(data_dict)
        df.convert_objects(convert_numeric=True)
        return df

    def _get_card_data(self, card):
        card_data = {
            "card_spent_time": float(card.spent_time) if card.spent_time else 0,
            "card_age": float(Decimal(card.age.seconds / 3600.0).quantize(Decimal("1.000"))),
            "num_forward_movements": float(card.number_of_forward_movements),
            "num_backward_movements": float(card.number_of_backward_movements),
            "num_comments": float(card.number_of_comments),
            "num_blocking_cards": card.blocking_cards.count(),
            "card_value": float(card.value) if card.value else 0,
            "length_name": len(card.name),
            "length_description": len(card.description),
            "num_members": card.members.count(),
            "num_labels": card.labels.count(),
            "has_red_label": 1 if card.labels.filter(color="red") else 0,
            "has_orange_label": 1 if card.labels.filter(color="orange") else 0,
            "has_yellow_label": 1 if card.labels.filter(color="yellow") else 0
        }

        # Member that work in this card
        for card_member in card.members.all():
            card_data[card_member.external_username] = 1
        for member in self.members:
            if not member.external_username in card_data:
                card_data[member.external_username] = 0

        # Creation list type
        for list_type in List.LIST_TYPES:
            card_data["creation_list_type_{0}".format(list_type)] = 0

        creation_list = card.creation_list
        if creation_list:
            card_data["creation_list_type_{0}".format(creation_list.type)] = 1

        return card_data
