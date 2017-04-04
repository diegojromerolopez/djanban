# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.forms import UpdateForecasterForm, BuildForecasterForm, TestForecasterForm
from djangotrellostats.apps.forecaster.models import Forecaster
from djangotrellostats.apps.forecaster.regression import OLS, GLS, WLS, GLSAR, QuantReg
from djangotrellostats.apps.members.models import Member
import numpy as np


@member_required
def index(request):
    forecasters = Forecaster.objects.all().order_by("board", "model")
    replacements = {"forecasters": forecasters}
    return render(request, "forecaster/index.html", replacements)


# Delete a Forecaster
class ForecasterDelete(DeleteView):
    model = Forecaster
    success_url = reverse_lazy('forecaster:index')
    template_name = "forecaster/delete.html"
    pk_url_kwarg = "forecaster_id"


@member_required
def test_forecaster_(request):
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
            return render(request, "forecaster/test.html", replacements)
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
        "summary": forecaster.results.summary(),
        "test_cards": test_cards,
        "total_error": total_error,
        "avg_error": avg_error,
        "std_dev_error": std_dev_error,
        "forecaster": forecaster
    })
    return render(request, "forecaster/test.html", replacements)


@member_required
def build_forecaster(request):
    if request.method == "POST":
        form = BuildForecasterForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("forecaster:index"))
    else:
        form = BuildForecasterForm()

    return render(request, "forecaster/build.html", {"form": form})


# Test a forecaster
@member_required
def test_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    if request.method == "POST":
        form = TestForecasterForm(request.POST)
        if form.is_valid():
            test_cards = forecaster.test_cards
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
            replacements = {
                "form": form, "forecaster": forecaster, "test_cards": test_cards,
                "total_error": total_error, "avg_error": avg_error, "std_dev_error": std_dev_error
            }
            return render(request, "forecaster/test.html", replacements)
    else:
        form = TestForecasterForm()

    return render(request, "forecaster/test.html", {"form": form})


# Update a forecaster
@member_required
def update_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    if request.method == "POST":
        form = UpdateForecasterForm(request.POST)
        if form.is_valid():
            form.save(forecaster)
            return HttpResponseRedirect(reverse("forecaster:index"))
    else:
        form = UpdateForecasterForm()

    return render(request, "forecaster/update.html", {"form": form, "forecaster": forecaster})


# View a forecaster
@member_required
def view_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    return render(request, "forecaster/view.html", {"forecaster": forecaster})
