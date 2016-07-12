from django.shortcuts import render

from djangotrellostats.apps.boards.models import Board


def index(request):
    member = None
    current_user = request.user
    if hasattr(current_user, "member") and current_user.member:
        member = current_user.member

    boards = Board.objects.all()

    replacements = {"boards": boards, "member": member}
    return render(request, "public/index.html", replacements)

