# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django import template
from django.template import loader, Context
from django.utils.text import slugify

register = template.Library()


@register.simple_tag(takes_context=True)
def async_include(context, template_path):
    t = loader.get_template('async_include/async_include_template_tag.html')

    print context

    replacements = {"template_path": template_path, "block_id": slugify(template_path), "context": {}}
    for context_item_name, context_item_value in context.items():
        replacements["context"][context_item_name] = context_item_value

    return t.render(Context(replacements))
