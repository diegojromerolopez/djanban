# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import models
from djangotrellostats.apps.niko_niko_calendar.models import DailyMemberMood


class NewDailyMemberMoodForm(models.ModelForm):
    class Meta:
        model = DailyMemberMood
        fields = ["mood"]

    def __init__(self, *args, **kwargs):
        super(NewDailyMemberMoodForm, self).__init__(*args, **kwargs)
        self.fields["mood"].label = "Mood on day {0}".format(self.instance.date.strftime("%Y-%m-%d"))

    def clean(self):
        cleaned_data = super(NewDailyMemberMoodForm, self).clean()
        member = self.instance.member
        date = self.instance.date
        if member.daily_member_moods.filter(date=date).exists():
            ValidationError(
                u"Member {0} has already a mood measurement on {1}".\
                format(member.trello_username, date.strftime("%Y-%m-%d"))
            )
        return cleaned_data
