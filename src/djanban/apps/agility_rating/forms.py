# -*- coding: utf-8 -*-


from django import forms
from django.forms import models

from djanban.apps.agility_rating.models import ProjectAgilityRating


# Project agility rating form
class ProjectAgilityRatingForm(models.ModelForm):
    class Meta:
        model = ProjectAgilityRating
        fields = ["personnel", "dynamism", "culture", "size", "criticality"]


# Project agility rating deletion form
class DeleteProjectAgilityRatingForm(forms.Form):
    confirmed = forms.BooleanField(
        label="Confirm you want to delete the agility rating"
    )
