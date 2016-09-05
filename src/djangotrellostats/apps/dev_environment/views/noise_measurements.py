# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from djangotrellostats.apps.dev_environment.forms import NewNoiseMeasurementForm, DeleteNoiseMeasurementForm
from djangotrellostats.apps.dev_environment.models import NoiseMeasurement


# View list of noise measurements
@login_required
def view_list(request):
    member = request.user.member
    noise_measurements = NoiseMeasurement.objects.all().order_by("-datetime")
    replacements = {"member": member, "noise_measurements": noise_measurements}
    return render(request, "dev_environment/noise_measurements/list.html", replacements)


# Create a new noise measurement
@login_required
def new(request):
    member = request.user.member

    noise_measurement = NoiseMeasurement(member=member)

    if request.method == "POST":
        form = NewNoiseMeasurementForm(request.POST, instance=noise_measurement)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("dev_environment:index"))
    else:
        form = NewNoiseMeasurementForm(instance=noise_measurement)

    return render(request, "dev_environment/noise_measurements/new.html", {"form": form, "member": member})


# Delete an noise_measurement
@login_required
def delete(request, noise_measurement_id):
    member = request.user.member
    noise_measurement = NoiseMeasurement.objects.get(id=noise_measurement_id)

    if request.method == "POST":
        form = DeleteNoiseMeasurementForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            noise_measurement.delete()
            return HttpResponseRedirect(reverse("dev_environment:index"))

    else:
        form = DeleteNoiseMeasurementForm()

    replacements = {"form": form, "member": member, "noise_measurement": noise_measurement}
    return render(request, "dev_environment/noise_measurements/delete.html", replacements)