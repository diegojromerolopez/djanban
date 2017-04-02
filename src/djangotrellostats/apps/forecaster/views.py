# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.regression import OLS, GLS, WLS, GLSAR, QuantReg
from djangotrellostats.apps.members.models import Member
import numpy as np


@login_required
def test_forecaster(request):
    cards = Card.objects.all()

    # Board selection
    boards = get_user_boards(request.user)
    board = None
    if request.GET.get("board") and boards.filter(id=request.GET.get("board")).exists():
        board = boards.get(id=request.GET.get("board"))
        cards = cards.filter(board=board)
        members = board.members.all()
    else:
        members = Member.objects.filter(boards__in=boards).distinct()

    method = request.GET.get("method")

    replacements = {
        "boards": boards, "method": method, "board": board,
    }

    # Forecasting method selection
    try:
        forecaster = None
        if method == "ols":
            forecaster = OLS(cards, members)
        elif method == "gls":
            forecaster = GLS(cards, members)
        elif method == "wls":
            forecaster = WLS(cards, members)
        elif method == "glsar":
            forecaster = GLSAR(cards, members)
        elif method == "quantreg":
            forecaster = QuantReg(cards, members)
        else:
            replacements["error"] = "Method {0} not recognized".format(method)
            return render(request, "forecaster/test.html", replacements)
    except AssertionError as e:
        replacements["error"] = e
        return render(request, "forecaster/test.html", replacements)

    # Run the forecasting method
    forecaster.run()

    # Test if the method is adjusted at least to the same data
    test_cards = forecaster.cards
    total_error = 0
    test_card_errors = []
    for test_card in test_cards:
        test_card_estimated_spent_time = float(forecaster.estimate_spent_time(test_card))
        test_card.estimated_spent_time = Decimal(test_card_estimated_spent_time).quantize(Decimal('1.000'))
        test_card.diff = test_card.spent_time - test_card.estimated_spent_time
        test_card.error = abs(test_card.diff)
        total_error += test_card.error
        test_card_errors.append(test_card.error)

    avg_error = np.mean(test_card_errors)
    std_dev_error = np.std(test_card_errors)

    # Template replacements
    replacements.update({
        "summary": forecaster.result.summary(),
        "test_cards": test_cards,
        "total_error": total_error,
        "avg_error": avg_error,
        "std_dev_error": std_dev_error,
        "forecaster": forecaster
    })
    return render(request, "forecaster/test.html", replacements)
