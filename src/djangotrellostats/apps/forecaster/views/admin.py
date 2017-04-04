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
def index(request):
    replacements = {}
    return render(request, "forecaster/index.html", replacements)


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
        if method == "ols":
            ForecasterClass = OLS
        elif method == "gls":
            ForecasterClass = GLS
        elif method == "wls":
            ForecasterClass = WLS
        elif method == "glsar":
            ForecasterClass = GLSAR
        elif method == "quantreg":
            ForecasterClass = QuantReg
        else:
            replacements["error"] = "Method {0} not recognized".format(method)
            return render(request, "forecaster/compute.html", replacements)
        forecaster = ForecasterClass(board=board, cards=cards, members=members)
    except AssertionError as e:
        replacements["error"] = e
        return render(request, "forecaster/test.html", replacements)

    # Run the forecasting method
    forecaster.run(save=False)

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


@login_required
def build_forecaster(request):
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
        if method == "ols":
            ForecasterClass = OLS
        elif method == "gls":
            ForecasterClass = GLS
        elif method == "wls":
            ForecasterClass = WLS
        elif method == "glsar":
            ForecasterClass = GLSAR
        elif method == "quantreg":
            ForecasterClass = QuantReg
        else:
            replacements["error"] = "Method {0} not recognized".format(method)
            return render(request, "forecaster/compute.html", replacements)
        forecaster = ForecasterClass(board=board, cards=cards, members=members)
    except AssertionError as e:
        replacements["error"] = e
        return render(request, "forecaster/compute.html", replacements)

    # Run the forecasting method
    forecaster.run(save=True)

    # Template replacements
    replacements.update({
        "summary": forecaster.result.summary(),
        "forecaster": forecaster
    })
    return render(request, "forecaster/compute.html", replacements)
