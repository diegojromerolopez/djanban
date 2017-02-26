# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader, Context


# Create your views here.
def get_template(request):
    path = request.POST.get("path")
    t = loader.get_template(path)
    c = Context({})
    replacements = {}
    return render(request, path, replacements)
