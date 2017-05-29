
from __future__ import unicode_literals

from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from djanban.apps.base.auth import user_is_member, get_user_boards
from djanban.apps.boards.models import List, Card
from djanban.apps.dev_environment.models import NoiseMeasurement
from djanban.apps.members.models import Member
from djanban.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


# Index view
def index(request):
    member = None
    boards = []
    member_multiboards = []
    team_mates = []
    current_user = request.user
    if user_is_member(current_user):
        member = current_user.member
        member_multiboards = member.multiboards. \
            filter(show_in_index=True, is_archived=False). \
            order_by("order", "name")

    lists = []
    if current_user.is_authenticated():
        team_mates = Member.get_user_team_mates(request.user)
        boards = get_user_boards(current_user).filter(is_archived=False).order_by("name")

    now = timezone.now()
    today = now.date()
    week_of_year = get_week_of_year(today)

    weeks_of_year = get_weeks_of_year_since_one_year_ago()

    replacements = {
        "any_card_has_value": Card.objects.filter(board__in=boards, value__isnull=False).exists(),
        "has_noise_measurements": NoiseMeasurement.objects.filter(Q(member__in=team_mates)|Q(member=member)).exists(),
        "weeks_of_year": weeks_of_year,
        "lists": lists,
        "boards": boards,
        "week_of_year": week_of_year,
        "member": member,
        "multiboards": member_multiboards,
        "developers": [member]+(list(member.team_mates.filter(is_developer=True)) if member else list(team_mates)),
        "downtime_developers": ([dev for dev in member.team_members.filter(is_developer=True) if dev.is_in_downtime]) if member else [],
        "pending_red_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="red").order_by("board__name", "name"),
        "pending_orange_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="orange").order_by("board__name", "name"),
        "pending_yellow_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="yellow").order_by("board__name", "name")
    }
    return render(request, "index/index.html", replacements)

