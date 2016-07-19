# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from djangotrellostats.apps.hourly_rates.forms import HourlyRateForm, DeleteHourlyRateForm
from djangotrellostats.apps.hourly_rates.models import HourlyRate


# View list of hourly rates
@login_required
def view_list(request):
    hourly_rates = HourlyRate.objects.all()
    replacements = {"hourly_rates": hourly_rates}
    return render(request, "hourly_rates/list.html", replacements)


# Create a new hourly rate
@login_required
def new(request):
    member = request.user.member
    hourly_rate = HourlyRate(creator=member)

    if request.method == "POST":
        form = HourlyRateForm(request.POST, instance=hourly_rate)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("hourly_rates:view_hourly_rates"))

    else:
        form = HourlyRateForm(instance=hourly_rate)

    return render(request, "hourly_rates/new.html", {"form": form, "member": member})


# Edit one hourly rate
@login_required
def edit(request, hourly_rate_id):
    member = request.user.member
    hourly_rate = HourlyRate.objects.get(id=hourly_rate_id)

    if request.method == "POST":
        form = HourlyRateForm(request.POST, instance=hourly_rate)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("hourly_rates:view_hourly_rates"))

    else:
        form = HourlyRateForm(instance=hourly_rate)

    return render(request, "hourly_rates/edit.html", {"form": form, "member": member, "hourly_rate": hourly_rate})


# Delete one hourly rate
@login_required
def delete(request, hourly_rate_id):
    member = request.user.member
    hourly_rate = HourlyRate.objects.get(id=hourly_rate_id)

    if request.method == "POST":
        form = DeleteHourlyRateForm(request.POST)

        if form.is_valid():
            hourly_rate.delete()
            return HttpResponseRedirect(reverse("hourly_rates:view_hourly_rates"))

    else:
        form = DeleteHourlyRateForm()

    return render(request, "hourly_rates/delete.html", {"form": form, "member": member, "hourly_rate": hourly_rate})
