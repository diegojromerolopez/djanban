
from __future__ import unicode_literals

from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone

from djangotrellostats.apps.base.auth import user_is_member, get_user_boards
from djangotrellostats.apps.boards.models import List, Card
from djangotrellostats.apps.members.models import Member
from djangotrellostats.utils.week import get_week_of_year, get_weeks_of_year_since_one_year_ago


# Index view
def index(request):
    member = None
    boards = []
    current_user = request.user
    if user_is_member(current_user):
        member = current_user.member

    lists = []
    if current_user.is_authenticated():
        boards = get_user_boards(current_user).order_by("name")
        now = timezone.now()
        # Card for each list possible choice
        for list_choice in List.LIST_TYPE_CHOICES:
            list_type_id = list_choice[0]
            list_type_name = list_choice[1]
            # Ignored and closed lists are not showed
            if list_type_id != "ignored" and list_type_id != "closed":
                list_active_cards = Card.get_user_cards(current_user)\
                    .filter(list__type=list_type_id).\
                    order_by("board_id", "position")

                # Do not show all done tasks. Show only tasks completed in the last 30 days
                if list_type_id == "done":
                    list_active_cards = list_active_cards.filter(last_activity_datetime__gte=now-timedelta(days=30))

                list_ = {
                    "id": list_type_id,
                    "type": list_type_id,
                    "name": list_type_name,
                    "active_cards": list_active_cards
                }
                lists.append(list_)

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
        "developers": member.team_mates.filter(is_developer=True),
        "downtime_developers": [dev for dev in member.team_mates.filter(is_developer=True) if dev.is_in_downtime],
        "pending_red_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="red").order_by("board__name", "name"),
        "pending_orange_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="orance").order_by("board__name", "name"),
        "pending_yellow_cards": Card.objects.filter(board__in=boards, list__type="ready_to_develop", is_closed=False, labels__color="yellow").order_by("board__name", "name")
    }
    return render(request, "index/index.html", replacements)

