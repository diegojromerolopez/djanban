from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.dev_environment.models import NoiseMeasurement, Interruption


@member_required
def index(request):
    member = request.user.member
    interruptions = Interruption.objects.all().order_by("-datetime")
    noise_measurements = NoiseMeasurement.objects.all().order_by("-datetime")
    summary_size = 5
    replacements = {
        "member": member,
        "summary_size": summary_size,
        "interruptions": interruptions[:summary_size], "num_interruptions": interruptions.count(),
        "noise_measurements": noise_measurements[:summary_size], "num_noise_measurements": noise_measurements.count()
    }
    return render(request, "dev_environment/index/index.html", replacements)