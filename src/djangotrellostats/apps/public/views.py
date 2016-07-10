from django.shortcuts import render

from djangotrellostats.apps.boards.models import Fetch, Board


def index(request):
    try:
        last_fetch = Fetch.last()
    except Fetch.DoesNotExist:
        last_fetch = None

    member = None
    current_user = request.user
    if hasattr(current_user, "member") and current_user.member:
        member = current_user.member

    boards = Board.objects.all()

    replacements = {"fetch": last_fetch, "boards": boards, "member": member}
    return render(request, "public/index.html", replacements)

