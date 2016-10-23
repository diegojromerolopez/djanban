from django.shortcuts import render
from django.utils import timezone

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards
from djangotrellostats.apps.members.models import Member
from djangotrellostats.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


# Index view
def index(request):
    member = None
    boards = []
    current_user = request.user
    if user_is_member(current_user):
        member = current_user.member

    if current_user.is_authenticated():
        boards = get_user_boards(current_user).order_by("name")

    now = timezone.now()
    today = now.date()
    week_of_year = get_week_of_year(today)

    weeks_of_year = get_weeks_of_year_since_one_year_ago()

    replacements = {
        "weeks_of_year": weeks_of_year,
        "boards": boards,
        "week_of_year": week_of_year,
        "member": member,
        "developers": Member.objects.filter(is_developer=True)
    }
    return render(request, "index/index.html", replacements)

