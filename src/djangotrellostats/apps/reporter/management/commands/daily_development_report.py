# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
import time
import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone

from djangotrellostats.apps.base.email import warn_administrators
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.niko_niko_calendar.models import DailyMemberMood
from djangotrellostats.apps.reporter.management.commands import daily_report
from django.core.mail import EmailMultiAlternatives


class Command(daily_report.Command):
    help = 'Daily report for developers'

    def handle(self, *args, **options):
        now = timezone.now()

        # Calling this management action without parameteres assume that date is today
        date = now.today()

        if options['date']:
            try:
                date = datetime.datetime.strptime(options["date"], "%Y-%m-%d")
            except ValueError:
                self.stderr.write(self.style.ERROR(u"Date {0} format is not valid".format(options["date"])))
                return None

        # If this day is holiday, don't send anything
        iso_weekday = date.isoweekday()
        if iso_weekday == 6 or iso_weekday == 7:
            self.stdout.write(
                self.style.SUCCESS(
                    u"Daily development reports for day {0} are not sent because that day is holiday".format(
                    date.strftime("%Y-%m-%d"))
                )
            )
            return False

        start = time.time()

        developers = Member.objects.filter(is_developer=True, on_holidays=False)
        try:
            for member in developers:
                if member.daily_spent_times.filter(date=date).count() > 0 and member.user:
                    daily_spent_times = member.daily_spent_times.filter(date=date).order_by("date", "member")
                    Command.send_daily_development_report(date, member, daily_spent_times)
                    self.stdout.write(self.style.SUCCESS(u"Daily report sent to developer {0}".format(member.user.email)))
                elif member.user:
                    self.stdout.write(
                        self.style.WARNING(u"Developer {0} has not worked on day {1}".format(member.user.email,
                                                                                         date.strftime("%Y-%m-%d")))
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(u"Developer {0} has no email".format(member.trello_username))
                    )

        except Exception as e:
            warn_administrators(subject=u"Error in Daily development report",
                                message=traceback.format_exc())
            self.stdout.write(self.style.ERROR(u"Error in the daily development report "))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(
            self.style.SUCCESS(u"Daily development reports for day {0} sent successfully to {1} developers in {2} s".format(
                date.strftime("%Y-%m-%d"), developers.count(), elapsed_time)
            )
        )

    # Send a daily report to one developer user
    @staticmethod
    def send_daily_development_report(date, developer_member, daily_spent_times):

        try:
            developer_mood = developer_member.daily_member_moods.get(date=date)
        except DailyMemberMood.DoesNotExist:
            developer_mood = None

        replacements = {
            "date": date,
            "developer": developer_member,
            "developer_mood": developer_mood,
            "developer_daily_spent_times": daily_spent_times.filter(member=developer_member)
        }

        txt_message = get_template('reporter/emails/daily_development_report.txt').render(replacements)
        html_message = get_template('reporter/emails/daily_development_report.html').render(replacements)

        subject = "[DjangoTrelloStats][DevReports] Daily development report of {0}".format(date.strftime("%Y-%m-%d"))

        csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})

        message = EmailMultiAlternatives(subject, txt_message, settings.EMAIL_HOST_USER, [developer_member.user.email])
        message.attach_alternative(html_message, "text/html")
        message.attach('spent_times-for-day-{0}.csv'.format(date.strftime("%Y-%m-%d")), csv_report, 'text/csv')
        message.send()
