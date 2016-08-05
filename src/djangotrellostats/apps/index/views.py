from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.week import get_iso_week_of_year, get_week_of_year


def index(request):
    member = None
    current_user = request.user
    if hasattr(current_user, "member") and current_user.member:
        member = current_user.member

    boards = Board.objects.all()

    now = timezone.now()
    today = now.date()
    week_of_year = get_week_of_year(today)

    weeks_of_year = [week_of_year]
    for i in range(1, 53):
        weeks_of_year.append(get_week_of_year(today-timedelta(days=7)*i))

    replacements = {
        "weeks_of_year": weeks_of_year,
        "boards": boards,
        "week_of_year": week_of_year,
        "member": member,
        "developers": Member.objects.filter(is_developer=True)
    }
    return render(request, "index/index.html", replacements)

