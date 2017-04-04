# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.models import Forecaster


@login_required
def estimate(request, card_id):
    card = Card.objects.get(id=card_id)
    estimations = []
    for forecaster in Forecaster.objects.all():
        estimated_spent_time = Decimal(forecaster.estimate_spent_time(card))
        estimations.append({
            "id": forecaster.id,
            "board": forecaster.board_id if forecaster.board else None,
            "model": forecaster.model,
            "formula": forecaster.formula,
            "estimation": estimated_spent_time
        })
    return JsonResponse(estimations, safe=False, encoder=DjangoJSONEncoder)
