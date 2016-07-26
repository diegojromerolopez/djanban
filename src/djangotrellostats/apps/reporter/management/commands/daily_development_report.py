import datetime
import time

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from django.utils import timezone

from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.members.models import Member
from djangotrellostats.apps.reporter.management.commands import daily_report


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

        start = time.time()

        daily_spent_times = DailySpentTime.objects.filter(date=date).order_by("date", "member")

        developers = Member.objects.filter(is_developer=True, on_holidays=False)
        for member in developers:
            if member.daily_spent_times.filter(date=date).count() > 0 and member.user:
                Command.send_daily_development_report(date, member, daily_spent_times)
                self.stdout.write(self.style.SUCCESS(u"Daily report sent to developer {0}".format(member.user.email)))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(
            self.style.SUCCESS(u"Daily reports for day {0} sent successfully to {1} developers in {2} s".format(
                date.strftime("%Y-%m-%d"), developers.count(), elapsed_time)
            )
        )

    # Send a daily report to one developer user
    @staticmethod
    def send_daily_development_report(date, developer_member, daily_spent_times):

        replacements = {
            "date": date,
            "developer": developer_member,
            "developer_daily_spent_times": daily_spent_times.filter(member=developer_member)
        }

        txt_message = get_template('reporter/emails/daily_development_report.txt').render(replacements)
        html_message = get_template('reporter/emails/daily_development_report.html').render(replacements)

        subject = "[DjangoTrelloStats][DevReports] Daily development report of {0}".format(date.strftime("%Y-%m-%d"))

        return send_mail(subject, txt_message, settings.EMAIL_HOST_USER, recipient_list=[developer_member.user.email],
                         fail_silently=False, html_message=html_message)