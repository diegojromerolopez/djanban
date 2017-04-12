# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecasters.regression.regressors import OLS, GLS, WLS, GLSAR, QuantReg, RLM
from djangotrellostats.apps.members.models import Member


# Regressor runner. Hides the complexity of selecting the right parameteres depending on the model.
class RegressorRunner(object):
    def __init__(self, name, model, board, member):
        self.name = name
        self.model = model
        self.board = board
        self.member = member

    def run(self):
        model = self.model.lower()
        if model == "ols":
            RegressorClass = OLS
        elif model == "gls":
            RegressorClass = GLS
        elif model == "wls":
            RegressorClass = WLS
        elif model == "glsar":
            RegressorClass = GLSAR
        elif model == "quantreg":
            RegressorClass = QuantReg
        elif model == "rlm":
            RegressorClass = RLM
        else:
            raise ValueError("Invalid RegressorClass")

        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        boards = get_user_boards(current_user)

        board = self.board
        member = self.member

        cards = Card.objects.all()
        if board:
            cards = cards.filter(board=board)
            members = board.members.all()
        elif member:
            cards = cards.filter(members__in=[member])
            members = []
        else:
            cards = cards.filter(board__in=boards)
            members = Member.objects.filter(boards__in=boards).distinct()

        regressor = RegressorClass(member=member, board=board, cards=cards, members=members,
                                   forecaster_name=self.name)
        return regressor.run(save=True)