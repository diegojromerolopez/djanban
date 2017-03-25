# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django import forms


class ReportRecipientForm(forms.ModelForm):
    class Meta:
        fields = ("first_name", "last_name", "email", "is_active", "boards")
