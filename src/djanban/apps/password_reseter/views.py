# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from audioop import reverse

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from djanban.apps.password_reseter.forms import RequestPasswordResetForm, ResetPasswordForm
from djanban.apps.password_reseter.models import PasswordResetRequest


# Request password reset
def request_password_reset(request):
    if request.method == "POST":
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            PasswordResetRequest.request_new_password(user, send_email=True)
            return render(request, "password_reseter/request_password_reset.html", {"requester_user": user})
    else:
        form = RequestPasswordResetForm()

    return render(request, "password_reseter/request_password_reset.html", {"form": form})


# Reset password
def reset_password(request, uuid):
    now = timezone.now()
    password_request = get_object_or_404(PasswordResetRequest, uuid=uuid, status="pending", limit_datetime__gt=now)
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get("password1")
            password_request.set_password(new_password, send_email=True)
            return render(request, "password_reseter/reset_password.html", {"requester_user": password_request.user})
    else:
        form = ResetPasswordForm()

    return render(request, "password_reseter/reset_password.html", {"form": form})