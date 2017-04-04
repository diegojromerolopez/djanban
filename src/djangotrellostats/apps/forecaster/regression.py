# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from decimal import Decimal

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels

from djangotrellostats.apps.boards.models import List
from djangotrellostats.apps.forecaster.models import Forecaster


# Execute a regression to the passed cards
from djangotrellostats.apps.forecaster.serializer import CardSerializer


class Regressor(object):

    def __init__(self, board, cards, members=None):
        self.board = board
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

    def fit(self, df, formula):
        raise NotImplementedError("Call here to statsmodels fit")

    def run(self, save=True):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.result = self.fit(df, formula)
        if save:
            model_name = self.__class__.__name__
            Forecaster.create_from_regression_results(
                board=self.board, model=model_name, formula=formula, results=self.result
            )
        return self.result

    def estimate_spent_time(self, card):
        return self.result.predict([self._get_card_data(card)])

    def _get_data_frame(self):
        data_dict = [self._get_card_data(card) for card in self.cards]
        df = pd.DataFrame(data_dict)
        df.convert_objects(convert_numeric=True)
        return df

    def _get_card_data(self, card):
        serializer = CardSerializer(card, self.members)
        return serializer.serialize()



# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Ordinary Least Squares method
class OLS(Regressor):

    def fit(self, df, formula):
        return smf.ols(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Generalized Least Squares method
class GLS(Regressor):

    def fit(self, df, formula):
        return smf.gls(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Generalized Least Squares method
class GLSAR(Regressor):

    def fit(self, df, formula):
        return smf.glsar(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using quantile regression model.
class QuantReg(Regressor):

    def get_formula(self):
        formula = """
            card_spent_time ~ card_age + num_time_measurements +
            num_forward_movements + num_backward_movements +
            num_comments + name_num_words
        """
        for member in self.members:
            formula += " + {0}".format(member.external_username)

        return formula

    def fit(self, df, formula):
        return smf.quantreg(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Weighted Least Squares method
class WLS(Regressor):

    def fit(self, df, formula):
        return smf.wls(formula=formula, data=df).fit()


