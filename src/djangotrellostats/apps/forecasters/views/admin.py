# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

import numpy as np
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.forecasters.forms import UpdateForecasterForm, BuildForecasterForm, TestForecasterForm, \
    FilterForecastersForm
from djangotrellostats.apps.forecasters.models import Forecaster


# List all forecasters
@member_required
def index(request):
    member = request.user.member

    form = FilterForecastersForm(request.GET)

    replacements = {"member": member, "form": form}
    template_path = "forecasters/index/without_board.html"

    if form.is_valid():
        forecasters = form.get_forecasters()
        user_boards = get_user_boards(request.user)
        if form.cleaned_data.get("board") and user_boards.filter(id=form.cleaned_data.get("board")).exists():
            board = user_boards.get(id=form.cleaned_data.get("board"))
            replacements["board"] = board
            template_path = "forecasters/index/with_board.html"
    else:
        forecasters = Forecaster.get_all_from_member(member)

    replacements["forecasters"] = forecasters

    return render(request, template_path, replacements)


# Delete a Forecaster
class ForecasterDelete(DeleteView):
    model = Forecaster
    success_url = reverse_lazy('forecasters:index')
    template_name = "forecasters/delete.html"
    pk_url_kwarg = "forecaster_id"

    def get_queryset(self):
        member = self.request.user.member
        return Forecaster.get_all_from_member(member)

    def get_context_data(self, *args, **kwargs):
        context = super(ForecasterDelete, self).get_context_data(*args, **kwargs)
        context["member"] = self.request.user.member
        return context


@member_required
def build_forecaster(request):
    member = request.user.member
    if request.method == "POST":
        form = BuildForecasterForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("forecasters:index"))
    else:
        form = BuildForecasterForm()

    return render(request, "forecasters/build.html", {"form": form, "member": member})


# Test a forecaster
@member_required
def test_forecaster(request, forecaster_id):
    member = request.user.member
    try:
        forecaster = Forecaster.get_all_from_member(member).get(id=forecaster_id)
    except Forecaster.DoesNotExist:
        raise Http404

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
                "total_error": total_error, "avg_error": avg_error, "std_dev_error": std_dev_error, "member": member
            }
            return render(request, "forecasters/test.html", replacements)
    else:
        form = TestForecasterForm()

    return render(request, "forecasters/test.html", {"form": form, "member": member, "forecaster": forecaster})


# Update a forecaster
@member_required
def update_forecaster(request, forecaster_id):
    member = request.user.member
    try:
        forecaster = Forecaster.get_all_from_member(member).get(id=forecaster_id)
    except Forecaster.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = UpdateForecasterForm(request.POST)
        if form.is_valid():
            form.save(forecaster)
            return HttpResponseRedirect(reverse("forecaster:index"))
    else:
        form = UpdateForecasterForm()

    return render(request, "forecasters/update.html", {"form": form, "forecaster": forecaster, "member": member})


# View a forecaster
@member_required
def view_forecaster(request, forecaster_id):
    member = request.user.member
    try:
        forecaster = Forecaster.get_all_from_member(member).get(id=forecaster_id)
    except Forecaster.DoesNotExist:
        raise Http404
    return render(request, "forecasters/view.html", {"forecaster": forecaster, "member": member})
