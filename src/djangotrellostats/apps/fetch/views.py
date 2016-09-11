# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.fetch.management.commands.fetch import Command


# Fetch all boards, its cards and its labels
@member_required
def fetch(request):
    member = request.user.member

    # Show fetch form
    if request.method == "GET":
        replacements = {"member": member}
        return render(request, "fetch/fetch.html", replacements)

    if not member.is_initialized():
        return render(request, "fetch/fetch_error.html",
                      context={"exception_message": u"Member {0} is not initialized".format(member.user.username)})

    try:
        fetch_command = Command()
        fetch_command.handle(member_trello_username=[member.trello_username])
    except Exception as e:
        return render(request, "fetch/fetch_error.html", context={"exception_message": e})

    return render(request, "fetch/fetch_success.html")
