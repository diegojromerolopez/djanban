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
from django.core.mail import EmailMultiAlternatives


class ReportCommand(BaseCommand):
    help = u'Base report for administrators'
    date_help_text = u"Date of the base report"

    def __init__(self):
        super(ReportCommand, self).__init__()
        self.date = None

    def add_arguments(self, parser):
        now = timezone.now()
        today = now.today()

        # Named (optional) arguments
        parser.add_argument(
            '--date',
            default=today.strftime("%Y-%m-%d"),
            help=self.__class__.date_help_text
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

        return date

    # Send reports to administrators
    def send_reports(self, daily_spent_times, subject,
                     txt_template_path, html_template_path, csv_file_name):

        # This report will be sent to each one of the administrators
        administrator_group = Group.objects.get(name=settings.ADMINISTRATOR_GROUP)
        administrator_users = administrator_group.user_set.all()
        for administrator_user in administrator_users:
            self.send_report(
                daily_spent_times, administrator_user, subject,
                txt_template_path, html_template_path, csv_file_name
            )
            self.stdout.write(self.style.SUCCESS(u"Report sent to {0}".format(administrator_user.email)))
        return administrator_users

    # Send a report to one administrator user
    def send_report(self, daily_spent_times, administrator_user, subject,
                    txt_template_path, html_template_path, csv_file_name):

        week = get_iso_week_of_year(self.date)
        replacements = {
            "date": self.date,
            "day": self.date.day,
            "week": week,
            "month": self.date.month,
            "year": self.date.year,
            "administrator": administrator_user,
            "boards": Board.objects.all(),
            "developer_members": Member.objects.filter(is_developer=True, on_holidays=False).order_by("trello_username"),
            "daily_spent_times": daily_spent_times,
        }

        txt_message = get_template(txt_template_path).render(replacements)
        html_message = get_template(html_template_path).render(replacements)

        csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})

        message = EmailMultiAlternatives(subject, txt_message, settings.EMAIL_HOST_USER, [administrator_user.email])
        message.attach_alternative(html_message, "text/html")
        message.attach(csv_file_name, csv_report, 'text/csv')
        message.send()

