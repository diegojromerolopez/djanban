# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.dev_environment.forms import NewInterruptionForm, DeleteInterruptionForm
from djangotrellostats.apps.dev_environment.models import Interruption


# View list of interruptions
@member_required
def view_list(request):
    member = request.user.member
    interruptions = Interruption.objects.all().order_by("-datetime")
    replacements = {"member": member, "interruptions": interruptions}
    return render(request, "dev_environment/interruptions/list.html", replacements)


# Create a new interruption
@member_required
def new(request):
    member = request.user.member

    interruption = Interruption(member=member)

    if request.method == "POST":
        form = NewInterruptionForm(request.POST, instance=interruption)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("dev_environment:index"))
    else:
        form = NewInterruptionForm(instance=interruption)

    return render(request, "dev_environment/interruptions/new.html", {"form": form, "member": member})


# Delete an interruption
@member_required
def delete(request, interruption_id):
    member = request.user.member
    interruption = Interruption.objects.get(id=interruption_id)

    if request.method == "POST":
        form = DeleteInterruptionForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            interruption.delete()
            return HttpResponseRedirect(reverse("dev_environment:index"))

    else:
        form = DeleteInterruptionForm()

    replacements = {"form": form, "member": member, "interruption": interruption}
    return render(request, "dev_environment/interruptions/delete.html", replacements)