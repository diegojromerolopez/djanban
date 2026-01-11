import importlib

from django import template


register = template.Library()


@register.simple_tag
def show_chart(module_name, name, *args, **kwargs):
    chart_module = importlib.import_module(f"djanban.apps.charts.{module_name}")
    if not hasattr(chart_module, name):
        return ""
    return getattr(chart_module, name, *args, **kwargs)
