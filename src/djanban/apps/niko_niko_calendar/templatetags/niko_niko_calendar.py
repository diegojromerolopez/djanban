# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from djanban.apps.niko_niko_calendar.models import DailyMemberMood


register = template.Library()


# Get the mood of a member in a date
@register.filter
def get_mood(member, date):
    try:
        return member.daily_member_moods.get(date=date)
    except DailyMemberMood.DoesNotExist:
        return ""
