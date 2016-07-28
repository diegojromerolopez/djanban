from django.shortcuts import render

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member


def index(request):
    member = None
    current_user = request.user
    if hasattr(current_user, "member") and current_user.member:
        member = current_user.member

    boards = Board.objects.all()

    replacements = {"boards": boards, "member": member, "developers": Member.objects.filter(is_developer=True)}
    return render(request, "index/index.html", replacements)

