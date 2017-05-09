# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import importlib
import inspect
from django import template
import datetime

from django.db.models import Sum

from djanban.apps.base.auth import get_user_boards
from djanban.apps.dev_times.models import DailySpentTime

register = template.Library()


@register.simple_tag
def show_chart(module_name, name, *args, **kwargs):
    chart_module = importlib.import_module("djanban.apps.charts.{0}".format(module_name))
    if not hasattr(chart_module, name):
        return ""
    return getattr(chart_module, name, *args, **kwargs)
