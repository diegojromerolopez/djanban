# -*- coding: utf-8 -*-

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from djangotrellostats.apps.base.forms import LoginForm


# User login
def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            django_login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = LoginForm()

    return render(request, "base/auth/login.html", {"form": form})


# User logout
@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse("index"))

