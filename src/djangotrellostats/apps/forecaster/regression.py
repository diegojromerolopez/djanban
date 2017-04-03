# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from decimal import Decimal

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels

from djangotrellostats.apps.boards.models import List


# Execute a regression to the passed cards
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

    def get_formula(self):
        formula = """
            card_spent_time ~ card_age + num_time_measurements +
            num_forward_movements + num_backward_movements +
            num_comments + name_num_words + name_length + description_num_words + description_length +
            num_members + num_mentioned_members
        """
        for member in self.members:
            formula += " + {0}".format(member.external_username)
        # Creation list type
        for list_type in List.LIST_TYPES:
            formula += " + creation_list_type_{0}".format(list_type)
        # Time this card has spent per list type
        for list_type in List.LIST_TYPES:
            formula += "+ time_in_list_type_{0}".format(list_type)

        return formula

    def run(self):
        raise NotImplementedError("run is not implemented")
        #df = self._get_data_frame()
        #formula = self.get_formula()
        #self.result = sm.ols(formula=formula, data=df).fit()

    def estimate_spent_time(self, card):
        return self.result.predict([self._get_card_data(card)])

    def _get_data_frame(self):
        data_dict = [self._get_card_data(card) for card in self.cards]
        df = pd.DataFrame(data_dict)
        df.convert_objects(convert_numeric=True)
        return df

    def _get_card_data(self, card):
        card_age_in_seconds_decimal = Decimal(card.age_in_board.seconds / 3600.0).quantize(Decimal("1.000"))
        card_age_in_seconds = float(card_age_in_seconds_decimal)
        num_forward_movements = 0
        if card.number_of_forward_movements > 0:
            num_forward_movements = float((card.number_of_forward_movements/card_age_in_seconds_decimal).quantize(Decimal("1.000")))
        num_backward_movements = 0
        if card.number_of_backward_movements > 0:
            num_backward_movements = float((card.number_of_backward_movements/card_age_in_seconds_decimal).quantize(Decimal("1.000")))
        name_num_words = len(re.split(r"\s+", card.name))
        description_num_words = len(re.split(r"\s+", card.name))
        card_data = {
            "card_spent_time": float(card.spent_time) if card.spent_time else 0,
            "num_time_measurements": card.daily_spent_times.count(),
            "card_age": card_age_in_seconds,
            "num_forward_movements": num_forward_movements,
            "num_backward_movements": num_backward_movements,
            "num_comments": float(card.number_of_comments),
            "num_blocking_cards": card.blocking_cards.count(),
            "card_value": float(card.value) if card.value else 0,
            "name_length": len(card.name),
            "name_num_words": name_num_words,
            "description_length": len(card.description),
            "description_num_words": description_num_words,
            "num_mentioned_members": card.number_of_mentioned_members,
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
            if member.external_username not in card_data:
                card_data[member.external_username] = 0

        # Creation list type
        for list_type in List.LIST_TYPES:
            card_data["creation_list_type_{0}".format(list_type)] = 0

        creation_list = card.creation_list
        if creation_list:
            card_data["creation_list_type_{0}".format(creation_list.type)] = 1

        # Time per list type
        time_per_list_type = card.time_in_each_list_type
        for list_type in List.LIST_TYPES:
            if list_type in time_per_list_type:
                card_data["time_in_list_type_{0}".format(list_type)] = time_per_list_type[list_type]
            else:
                card_data["time_in_list_type_{0}".format(list_type)] = 0

        return card_data


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Ordinary Least Squares method
class OLS(Regressor):

    def __init__(self, cards, members=None):
        super(OLS, self).__init__(cards, members)

    def run(self):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = smf.ols(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Generalized Least Squares method
class GLS(Regressor):

    def __init__(self, cards, members=None):
        super(GLS, self).__init__(cards, members)

    def run(self):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = smf.gls(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Generalized Least Squares method
class GLSAR(Regressor):

    def __init__(self, cards, members=None):
        super(GLSAR, self).__init__(cards, members)

    def run(self):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = smf.glsar(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using quantile regression model.
class QuantReg(Regressor):

    def __init__(self, cards, members=None):
        super(QuantReg, self).__init__(cards, members)

    def get_formula(self):
        formula = """
            card_spent_time ~ card_age + num_time_measurements +
            num_forward_movements + num_backward_movements +
            num_comments + name_num_words
        """
        for member in self.members:
            formula += " + {0}".format(member.external_username)

        return formula

    def run(self):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = smf.quantreg(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Weighted Least Squares method
class WLS(Regressor):

    def __init__(self, cards, members=None):
        super(WLS, self).__init__(cards, members)

    def run(self):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = smf.wls(formula=formula, data=df).fit()

