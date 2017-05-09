
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone

from djanban.apps.base.auth import user_is_member, get_user_boards
from djanban.apps.boards.models import List, Card
from djanban.apps.members.models import Member
from djanban.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


# Index view
def index(request):
    member = None
    boards = []
    member_multiboards = []
    current_user = request.user
    if user_is_member(current_user):
        member = current_user.member
        member_multiboards = member.created_multiboards. \
            filter(show_in_index=True, is_archived=False). \
            order_by("order", "name")

    lists = []
    if current_user.is_authenticated():
        boards = get_user_boards(current_user).filter(is_archived=False).order_by("name")

    now = timezone.now()
    today = now.date()
    week_of_year = get_week_of_year(today)

    weeks_of_year = get_weeks_of_year_since_one_year_ago()

    replacements = {
        "weeks_of_year": weeks_of_year,
        "lists": lists,
        "boards": boards,
        "week_of_year": week_of_year,
        "member": member,
        "multiboards": member_multiboards,
        "developers": member.team_mates.filter(is_developer=True) if member else [],
        "downtime_developers": ([dev for dev in member.team_mates.filter(is_developer=True) if dev.is_in_downtime]) if member else [],
        "pending_red_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="red").order_by("board__name", "name"),
        "pending_orange_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="orange").order_by("board__name", "name"),
        "pending_yellow_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="yellow").order_by("board__name", "name")
    }
    return render(request, "index/index.html", replacements)

