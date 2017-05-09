from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from djanban.apps.base.auth import get_user_boards, user_is_member
from djanban.apps.dev_environment.models import Interruption
from djanban.apps.dev_environment.models import NoiseMeasurement
from djanban.apps.members.models import Member


# View the slideshow
@login_required
def view(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member

    boards = get_user_boards(request.user).\
        filter(show_on_slideshow=True).\
        exclude(last_fetch_datetime=None).\
        order_by("-last_activity_datetime")

    replacements = {
        "simple_carousel": True if request.GET.get("simple") == "1" else False,
        "column_mode": "single_column" if request.GET.get("column_mode") == "1" else "normal",
        "member": member,
        "boards": boards,
        "members": Member.objects.filter(boards__in=boards).distinct(),
        "interruptions": Interruption.objects.all(),
        "noise_measurements": NoiseMeasurement.objects.all()
    }
    return render(request, "slideshow/view.html", replacements)

