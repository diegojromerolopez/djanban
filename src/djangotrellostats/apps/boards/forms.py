# -*- coding: utf-8 -*-

import re
from django.forms import models
from djangotrellostats.apps.boards.models import Board


# Board edition form
class EditBoardForm(models.ModelForm):
    class Meta:
        model = Board
        fields = ["has_to_be_fetched", "comments", "estimated_number_of_hours",
                  "percentage_of_completion", "hourly_rates",
                  "enable_public_access", "public_access_code"]

    def __init__(self, *args, **kwargs):
        super(EditBoardForm, self).__init__(*args, **kwargs)
        self.fields["hourly_rates"].help_text = u"Please, select the hourly rates this board uses. System does not " \
                                                u"check if there is overlapping, so take care."

    def clean(self):
        cleaned_data = super(EditBoardForm, self).clean()
        return cleaned_data

