from django.core.exceptions import ValidationError
from django.forms import models, DateInput
from djanban.apps.hourly_rates.models import HourlyRate
from django import forms
from djanban.utils.forms.widgets import Html5DateInput


# Hourly rate creation and edition form
class HourlyRateForm(models.ModelForm):
    class Meta:
        model = HourlyRate
        fields = ["name", "start_date", "end_date", "amount", "is_active"]

    def __init__(self, *args, **kwargs):
        super(HourlyRateForm, self).__init__(*args, **kwargs)
        date_input_formats = ('%d/%m/%Y','%Y/%m/%d')
        self.fields["start_date"].widget.format='%Y/%m/%d'
        self.fields["start_date"].input_formats = date_input_formats
        self.fields["end_date"].input_formats = date_input_formats
        self.fields["end_date"].widget.format = '%Y/%m/%d'
        if self.instance:
            self.fields["start_date"].initial = self.instance
            self.fields["end_date"].initial = self.instance

    def clean(self):
        cleaned_data = super(HourlyRateForm, self).clean()
        if cleaned_data.get("end_date") and cleaned_data.get("start_date") > cleaned_data.get("end_date"):
            raise ValidationError(u"Start date can't be greater that end date")
        return cleaned_data


class DeleteHourlyRateForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Please confirm you really want to do this action", required=True)
