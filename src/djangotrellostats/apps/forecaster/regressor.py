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
        return pd.DataFrame(data_dict)

    def _get_card_data(self, card):
        card_data = {
            "card_spent_time": card.spent_time if card.spent_time else Decimal("0"),
            "card_age": Decimal(card.age.seconds / 3600.0).quantize(Decimal("1.000")),
            "num_forward_movements": card.number_of_forward_movements,
            "num_backward_movements": card.number_of_backward_movements,
            "num_comments": card.number_of_comments,
            "num_blocking_cards": Decimal(card.blocking_cards.count()),
            "card_value": card.value if card.value else Decimal("0"),
            "length_name": Decimal(len(card.name)),
            "length_description": Decimal(len(card.description)),
            "num_members": Decimal(card.members.count()),
            "num_labels": Decimal(card.labels.count()),
            "has_red_label": Decimal(1) if card.labels.filter(color="red") else Decimal(0),
            "has_orange_label": Decimal(1) if card.labels.filter(color="orange") else Decimal(0),
            "has_yellow_label": Decimal(1) if card.labels.filter(color="yellow") else Decimal(0)
        }

        float_card_data = {}
        for card_attr, card_datum in card_data.items():
            float_card_data[card_attr] = float(card_datum)

        # Member that work in this card
        for card_member in card.members.all():
            float_card_data[card_member.external_username] = 1
        for member in self.members:
            if not member.external_username in card_data:
                float_card_data[member.external_username] = 0

        # Creation list type
        for list_type in List.LIST_TYPES:
            float_card_data["creation_list_type_{0}".format(list_type)] = 0

        creation_list = card.creation_list
        if creation_list:
            float_card_data["creation_list_type_{0}".format(creation_list.type)] = 1

        return float_card_data
