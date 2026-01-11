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
            'end_date': forms.SelectDateWidget(empty_label="Until now"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("end_date") and cleaned_data.get("start_date") > cleaned_data.get("end_date"):
            raise ValidationError("Start date can't be greater that end date")
        return cleaned_data


class DeleteHourlyRateForm(forms.Form):
    confirmed = forms.BooleanField(label="Please confirm you really want to do this action", required=True)
