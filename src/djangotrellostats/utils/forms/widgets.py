# -*- coding: utf-8 -*-

from django import forms


class Html5DateInput(forms.DateInput):
    input_type = 'date'
