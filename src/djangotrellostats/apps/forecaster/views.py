# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.linear_regression import LinearRegressor


@login_required
def test_forecaster(request):
    cards = Card.objects.all()

    # Board selection
    boards = get_user_boards(request.user)
    board = None
    if request.GET.get("board") and boards.filter(id=request.GET.get("board")).exists():
        board = boards.get(id=request.GET.get("board"))
        cards = cards.filter(board=board)

    method = request.GET.get("method")

    replacements = {
        "boards": boards, "method": method, "board": board,
    }

    # Forecasting method selection
    try:
        forecaster = None
        if method == "linear_regression":
            forecaster = LinearRegressor(cards)
        else:
            replacements["error"] = "Method {0} not recognized".format(method)
            return render(request, "forecaster/test.html", {"error": replacements})
    except AssertionError as e:
        replacements["error"] = e
        return render(request, "forecaster/test.html", replacements)

    # Run the forecasting method
    forecaster.run()

    # Test if the method is adjusted at least to the same data
    test_cards = forecaster.cards
    total_error = 0
    for test_card in test_cards:
        test_card.estimated_spent_time = Decimal(forecaster.estimate_spent_time(test_card)).quantize(Decimal('1.000'))
        test_card.error = abs(test_card.spent_time - test_card.estimated_spent_time)
        total_error += test_card.error

    # Template replacements
    replacements.update({
        "test_cards": test_cards, "total_error": total_error,
        "forecaster": forecaster
    })
    return render(request, "forecaster/test.html", replacements)
