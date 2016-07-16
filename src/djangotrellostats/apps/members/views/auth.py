# -*- coding: utf-8 -*-

from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render

from djangotrellostats.apps.members.forms import SignUpForm, LoginForm


# User registration
@transaction.atomic
def signup(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            member = form.save(commit=True)
            user = authenticate(username=member.user.username, password=form.data["password1"])
            if user and user is not None:
                django_login(request, user)
                return HttpResponseRedirect(reverse("index"))

    else:
        form = SignUpForm()

    return render(request, "members/signup.html", {"form": form})


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

    return render(request, "members/login.html", {"form": form})


# User logout
@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse("index"))





