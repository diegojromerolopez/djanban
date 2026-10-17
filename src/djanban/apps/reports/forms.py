# -*- coding: utf-8 -*-


from django import forms


class ReportRecipientForm(forms.ModelForm):
    class Meta:
        fields = ("first_name", "last_name", "email", "is_active", "boards")
