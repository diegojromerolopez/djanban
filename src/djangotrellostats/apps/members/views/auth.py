# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template

from djangotrellostats.apps.members.forms import SignUpForm, LoginForm, ResetPasswordForm


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


# Resets user password and send it to user
def reset_password(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data["member"]
            password = member.reset_password()
            _send_new_password_to_member(member, password)
            return HttpResponseRedirect(reverse("members:reset_password_success"))
    else:
        form = ResetPasswordForm()
    return render(request, "members/reset_password.html", {"form": form})


# Send a new password to the member
def _send_new_password_to_member(member, password):
    replacements = {"member": member, "password": password}

    txt_message = get_template('members/emails/reset_password.txt').render(replacements)
    html_message = get_template('members/emails/reset_password.html').render(replacements)

    subject = "Reset password"

    return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[member.user.email],
                     fail_silently=False, html_message=html_message)

