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
    help = 'Monthly report for administrators'

    def add_arguments(self, parser):
        now = timezone.now()
        today = now.today()

        # Named (optional) arguments
        parser.add_argument(
            '--date',
            default=today.strftime("%Y-%m-%d"),
            help='Send the monthly report of the month of this date to the administrators',
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

        month = date.month
        year = date.year

        start = time.time()

        daily_spent_times = DailySpentTime.objects.filter(date__month=month, date__year=year).order_by("date", "member")

        # This daily report will be sent to each one of the administrators
        administrator_group = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
        administrator_users = administrator_group.user_set.all()
        for administrator_user in administrator_users:
            Command.send_weekly_report(month, year, administrator_user, daily_spent_times)
            self.stdout.write(self.style.SUCCESS(u"Monthly report sent to {0}".format(administrator_user.email)))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(
            self.style.SUCCESS(u"Monthly reports for month {0}/{1} sent successfully to {2} in {3} s".format(
                year, month, administrator_users.count(), elapsed_time)
            )
        )

    # Send a monthly report to one administrator user
    @staticmethod
    def send_weekly_report(month, year, administrator_user, daily_spent_times):

        replacements = {
            "month": month,
            "year": year,
            "administrator": administrator_user,
            "boards": Board.objects.all(),
            "developer_members": Member.objects.filter(is_developer=True, on_holidays=False).order_by("trello_username"),
            "daily_spent_times": daily_spent_times,
        }

        txt_message = get_template('reporter/emails/monthly_report.txt').render(replacements)
        html_message = get_template('reporter/emails/monthly_report.html').render(replacements)

        subject = "[DjangoTrelloStats][Reports] Monthly report of {0}/{1}".format(year, month)

        return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[administrator_user.email],
                         fail_silently=False, html_message=html_message)
