# -*- coding: utf-8 -*-

import numpy


def avg(queryset, attribute):
    values = _get_item_list(queryset, attribute)
    if len(values) == 0:
        return None
    return numpy.mean(values)


def std_dev(queryset, attribute):
    values = _get_item_list(queryset, attribute)
    if len(values) == 0:
        return None
    return numpy.std(values, axis=0)


def _get_item_list(queryset, attribute):
    value_list = []
    for item in queryset:
        value = getattr(item, attribute)
        if value is not None:
            value_list.append(value)
    return value_list
