# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from djanban.apps.members.forms import JiraSignUpForm, TrelloSignUpForm, LocalSignUpForm, ResetPasswordForm


# Local user registration
def signup(request):
    return render(request, "members/signup/main.html")


# Local user registration
@transaction.atomic
def local_signup(request):

    if request.method == "POST":
        form = LocalSignUpForm(request.POST)

        if form.is_valid():
            member = form.save(commit=True)
            user = authenticate(username=member.user.username, password=form.data["password1"])
            if user and user is not None:
                django_login(request, user)
                return HttpResponseRedirect(reverse("index"))

    else:
        form = LocalSignUpForm()

    return render(request, "members/signup/backends/local_signup.html", {"form": form})


# Trello user registration
@transaction.atomic
def trello_signup(request):

    if request.method == "POST":
        form = TrelloSignUpForm(request.POST)

        if form.is_valid():
            member = form.save(commit=True)
            user = authenticate(username=member.user.username, password=form.data["password1"])
            if user and user is not None:
                django_login(request, user)
                return HttpResponseRedirect(reverse("index"))

    else:
        form = TrelloSignUpForm()

    return render(request, "members/signup/backends/trello_signup.html", {"form": form})


# Jira user registration
@transaction.atomic
def jira_signup(request):

    if request.method == "POST":
        form = JiraSignUpForm(request.POST)

        if form.is_valid():
            member = form.save(commit=True)
            user = authenticate(username=member.user.username, password=form.data["password1"])
            if user and user is not None:
                django_login(request, user)
                return HttpResponseRedirect(reverse("index"))

    else:
        form = JiraSignUpForm()

    return render(request, "members/signup/backends/jira_signup.html", {"form": form})


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

