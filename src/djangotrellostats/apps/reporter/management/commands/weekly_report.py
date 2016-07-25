import time

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import get_template

from djangotrellostats.apps.boards.models import Board
from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member

import datetime

from djangotrellostats.apps.week import get_iso_week_of_year


class Command(BaseCommand):
    help = 'Weekly report for administrators'

    def add_arguments(self, parser):
        now = timezone.now()
        today = now.today()

        # Named (optional) arguments
        parser.add_argument(
            '--date',
            default=today.strftime("%Y-%m-%d"),
            help='Send the weekly report of the week of this date to the administrators',
        )

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

        week = get_iso_week_of_year(date)
        year = date.year

        start = time.time()

        daily_spent_times = DailySpentTime.objects.filter(week_of_year=week).order_by("date", "member")

        # This daily report will be sent to each one of the administrators
        administrator_group = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
        administrator_users = administrator_group.user_set.all()
        for administrator_user in administrator_users:
            Command.send_weekly_report(week, year, administrator_user, daily_spent_times)
            self.stdout.write(self.style.SUCCESS(u"Weekly report sent to {0}".format(administrator_user.email)))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(
            self.style.SUCCESS(u"Weekly reports for week {0}W-{1} sent successfully to {2} in {3} s".format(
                week, year, administrator_users.count(), elapsed_time)
            )
        )

    # Send a weekly report to one administrator user
    @staticmethod
    def send_weekly_report(week, year, administrator_user, daily_spent_times):

        replacements = {
            "week": week,
            "year": year,
            "administrator": administrator_user,
            "boards": Board.objects.all(),
            "developer_members": Member.objects.filter(is_developer=True, on_holidays=False).order_by("trello_username"),
            "daily_spent_times": daily_spent_times,
        }

        txt_message = get_template('reporter/emails/weekly_reporter.txt').render(replacements)
        html_message = get_template('reporter/emails/weekly_reporter.html').render(replacements)

        subject = "[DjangoTrelloStats][Reports] Weekly report of {0}W-{1}".format(week, year)

        return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[administrator_user.email],
                         fail_silently=False, html_message=html_message)