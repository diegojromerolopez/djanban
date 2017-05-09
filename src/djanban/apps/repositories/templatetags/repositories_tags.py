# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def filter_error_messages_by_file(error_messages, file):
    return error_messages.filter(commit_file=file)