# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pandas as pd
import  statsmodels.nonparametric.kernel_regression as kr
import statsmodels.formula.api as smf

from djangotrellostats.apps.boards.models import List
from djangotrellostats.apps.forecasters.models import Forecaster
from djangotrellostats.apps.forecasters.serializer import CardSerializer


# Regression models that exist in this module
REGRESSION_MODELS = (
    ("ols", "OLS Regression"),
    ("wls", "WLS Regression"),
    ("gls", "GLS Regression"),
    ("glsar", "GLSAR Regression"),
    ("quantreg", "Quantile Regression"),
    ("rlm", "Robust Linear Model Regression")
)


# Regressor class. It is used to build regression models.
# Execute a regression to the passed cards
class Regressor(object):

    # Construct the Regressor
    # Board is optional
    def __init__(self, member, board, cards, forecaster_name, members=None):
        self.member = member
        self.board = board
        self.results = None
        # We are going to make the regression with the active done cards that have consumed some time
        self.cards = cards\
            .filter(is_closed=False, spent_time__gt=0, list__type="done")
        self.forecaster_name = forecaster_name
        if members:
            self.members = members
        else:
            self.members = []
        if not self.cards.exists():
            raise AssertionError(u"There are no cards")

    # Returns the formula used in the regression
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
        for list_type in List.ACTIVE_LIST_TYPES:
            formula += " + creation_list_type_{0}".format(list_type)
        # Time this card has spent per list type
        for list_type in List.ACTIVE_LIST_TYPES:
            formula += "+ time_in_list_type_{0}".format(list_type)

        return formula

    # Fit the regression model
    # Reimplement this method in successive regression models
    def fit(self, df, formula):
        raise NotImplementedError("Call here to statsmodels fit")

    # Execute the regression
    # If save parameter is passed, save the regression model in database
    def run(self, save=True):
        df = self._get_data_frame()
        formula = self.get_formula()
        self.results = self.fit(df, formula)
        if save:
            Forecaster.create_from_regressor(self, name=self.forecaster_name)
        return self.results

    # Direct estimation from computed results
    # Use only in tests
    def estimate_spent_time(self, card):
        return self.results.predict([self._get_card_data(card)])

    # Convert all the cards in a Panda DataFrame
    def _get_data_frame(self):
        data_dict = [self._get_card_data(card) for card in self.cards]
        df = pd.DataFrame(data_dict)
        df.convert_objects(convert_numeric=True)
        return df

    # Serialize card for DataFrame creation
    def _get_card_data(self, card):
        serializer = CardSerializer(card, self.members)
        return serializer.serialize()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Ordinary Least Squares method
class OLS(Regressor):
    def get_formula(self):
        formula = super(OLS, self).get_formula()
        return formula

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


# Robust Linear Model regression generator
class RLM(Regressor):
    def fit(self, df, formula):
        return smf.rlm(formula=formula, data=df).fit()


# Produce a linear regression of the spent time of the cards of the boards
# that are passed as parameter to this class using Weighted Least Squares method
class WLS(Regressor):

    def fit(self, df, formula):
        return smf.wls(formula=formula, data=df).fit()


