
from __future__ import unicode_literals
import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils import timezone

from djanban.apps.boards.models import Board
from djanban.apps.members.models import Member
from djanban.apps.reports.models import ReportRecipient
from djanban.utils.week import get_iso_week_of_year, start_of_week_of_year, end_of_week_of_year


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
        report_recipients = ReportRecipient.objects.filter(is_active=True)
        for report_recipient in report_recipients:
            self.send_report(
                daily_spent_times, report_recipient, subject,
                txt_template_path, html_template_path, csv_file_name
            )
            self.stdout.write(self.style.SUCCESS(u"Report sent to {0}".format(report_recipient.email)))
        return report_recipients

    # Send a report to one administrator user
    def send_report(self, daily_spent_times, report_recipient, subject,
                    txt_template_path, html_template_path, csv_file_name):

        week = get_iso_week_of_year(self.date)
        start_week_date = start_of_week_of_year(week, self.date.year)
        end_week_date = end_of_week_of_year(week, self.date.year)
        replacements = {
            "start_week_date": start_week_date,
            "end_week_date": end_week_date,
            "date": self.date,
            "day": self.date.day,
            "week": week,
            "month": self.date.month,
            "year": self.date.year,
            "report_recipient": report_recipient,
            "boards": report_recipient.boards.all(),
            "developer_members": Member.objects.filter(is_developer=True, on_holidays=False).order_by("trello_member_profile__username"),
            "daily_spent_times": daily_spent_times,
        }

        txt_message = get_template(txt_template_path).render(replacements)
        html_message = get_template(html_template_path).render(replacements)

        csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})

        message = EmailMultiAlternatives(subject, txt_message, settings.EMAIL_HOST_USER, [report_recipient.email])
        message.attach_alternative(html_message, "text/html")
        message.attach(csv_file_name, csv_report, 'text/csv')
        message.send()

