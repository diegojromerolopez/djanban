# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import models
from djanban.apps.hourly_rates.models import HourlyRate
from django import forms


# Hourly rate creation and edition form
class HourlyRateForm(models.ModelForm):
    class Meta:
        model = HourlyRate
        fields = ["name", "start_date", "end_date", "amount", "is_active"]
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(empty_label=u"Until now"),
        }

    def __init__(self, *args, **kwargs):
        super(HourlyRateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(HourlyRateForm, self).clean()
        if cleaned_data.get("end_date") and cleaned_data.get("start_date") > cleaned_data.get("end_date"):
            raise ValidationError(u"Start date can't be greater that end date")
        return cleaned_data


class DeleteHourlyRateForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Please confirm you really want to do this action", required=True)
