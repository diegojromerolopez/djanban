# -*- coding: utf-8 -*-

import re
from django.forms import models

from djanban.apps.agility_rating.models import ProjectAgilityRating
from djanban.apps.boards.models import Board
from django import forms


# Project agility rating form
class ProjectAgilityRatingForm(models.ModelForm):
    class Meta:
        model = ProjectAgilityRating
        fields = ["personnel", "dynamism", "culture", "size", "criticality"]


# Project agility rating deletion form
class DeleteProjectAgilityRatingForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete the agility rating")
