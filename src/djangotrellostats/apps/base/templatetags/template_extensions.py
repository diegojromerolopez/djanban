# -*- coding: utf-8 -*-

import inspect
from django import template


register = template.Library()


# Each one of the arguments of a method
# It will be called jointly with call filter.
# See filter for more information about its use.
#
# Inspired by http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
@register.filter(is_safe=True)
def arg(callable_dict, _arg):
    # Append to the arguments of the callable method
    callable_dict["args"].append(_arg)

    # If it is the last argument, call the callable with the arguemnts
    if len(callable_dict["args"]) == callable_dict["num_arguments"] - 1:
        _callable = callable_dict["callable"]
        return _callable(*callable_dict["args"])

    # Otherwise, return the dict we append the new argument
    return callable_dict


# In case it is needed to ignore default parameters
#
# Inspired by http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
@register.filter(is_safe=True)
def end_call(callable_dict):
    _callable = callable_dict["callable"]
    return _callable(*callable_dict["args"])


# Filter for calling a method object
#
# Use:
#
# If it has all the parameters of the prototype of the method:
# {{<object>|call:"<method_name>"|arg:<arg1>|arg:<arg2>|...|arg:<argN>}}
#
# If it has default parameters i in arg_i > i:
# {{<object>|call:"<method_name>"|arg:<arg1>|arg:<arg2>|...|arg:<argI>|end_call}}
#
# Inspired by http://www.sprklab.com/notes/13-passing-arguments-to-functions-in-django-template
#
@register.filter(is_safe=True)
def call(_object, method_name):
    # When the object has not a method called "method_name", returns None to don't break the templates
    if not hasattr(_object, method_name):
        return None

    # Getting the callable object of this method
    callable_method = getattr(_object, method_name)

    # Getting the number of arguments or this callable object
    arg_spec = inspect.getargspec(callable_method)
    num_arguments = len(arg_spec.args)

    # If there is only one argument, it is self, so call the callable object and return the result
    if num_arguments == 1:
        return callable_method()

    # Otherwise, return a dict with all the data needed to pass the other arguments to the callable
    return {"callable": callable_method, "num_arguments": num_arguments, "args": []}


# Subtract two values
@register.filter
def subtract(value, argument):
    return value - argument


# Multiply two values
@register.filter
def multiply(value, argument):
    return value * argument