# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy

from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.urls import reverse
from django.utils import timezone

from djanban.apps.base.auth import get_user_boards, user_is_member
from djanban.apps.base.decorators import member_required
from djanban.apps.members.models import Member
from djanban.apps.niko_niko_calendar.forms import NewDailyMemberMoodForm
from djanban.apps.niko_niko_calendar.models import DailyMemberMood


# Show the niko-niko calendar. List the mood of the team.
@login_required
def view_calendar(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member

    boards = get_user_boards(request.user)
    members = Member.objects.filter(boards__in=boards).distinct().filter(is_developer=True).order_by("id")

    min_date = DailyMemberMood.objects.filter(member__in=members).aggregate(min_date=Min("date"))["min_date"]
    max_date = DailyMemberMood.objects.filter(member__in=members).aggregate(max_date=Max("date"))["max_date"]

    dates = []
    if min_date and max_date:
        date_i = copy.deepcopy(min_date)
        while date_i <= max_date:
            # Only add date when there are mood measurements
            if DailyMemberMood.objects.filter(date=date_i, member__in=members).exists():
                dates.append(date_i)
            date_i += timedelta(days=1)

    replacements = {"member": member, "members": members, "dates": dates}
    return render(request, "niko_niko_calendar/calendar.html", replacements)


# Create a new mood measurement for the niko-niko calendar
@member_required
def new_mood_measurement(request):
    member = request.user.member
    today = timezone.now().date()

    daily_member_mood = DailyMemberMood(member=member, date=today)

    if request.method == "POST":
        form = NewDailyMemberMoodForm(request.POST, instance=daily_member_mood)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("niko_niko_calendar:view_calendar"))
    else:
        form = NewDailyMemberMoodForm(instance=daily_member_mood)

    replacements = {"form": form, "today": today, "member": member, "date": today}
    return render(request, "niko_niko_calendar/new_mood_measurement.html", replacements)

