from __future__ import unicode_literals

import time
from djanban.apps.dev_times.models import DailySpentTime
from djanban.apps.reporter.management.report_command import ReportCommand


class Command(ReportCommand):
    help = 'Daily report for administrators'
    date_help_text = 'Send the daily report for this date to the administrators'

    def handle(self, *args, **options):
        self.date = super(Command, self).handle(*args, **options)

        # If this day is holiday, don't send anything
        iso_weekday = self.date.isoweekday()
        if iso_weekday == 6 or iso_weekday == 7:
            self.stdout.write(
                self.style.SUCCESS(u"Daily reports for day {0} are not sent because that day is holiday".format(
                    self.date.strftime("%Y-%m-%d"))
                )
            )
            return False

        start = time.time()

        daily_spent_times = DailySpentTime.objects.filter(date=self.date).order_by("date", "member")

        subject = "[Djanban][Reports] Daily report of {0}".format(self.date.strftime("%Y-%m-%d"))
        txt_template_path = 'reporter/emails/daily_report.txt'
        html_template_path = 'reporter/emails/daily_report.html'
        csv_file_name = 'spent_times-for-day-{0}.csv'.format(self.date.strftime("%Y-%m-%d"))

        report_recipient = self.send_reports(daily_spent_times, subject,
                                                txt_template_path, html_template_path, csv_file_name)
        self.stdout.write(self.style.SUCCESS(u"Daily reports sent to {0} administrators".format(report_recipient.count())))

        end = time.time()
        elapsed_time = end-start

        self.stdout.write(
            self.style.SUCCESS(u"Daily reports for day {0} sent successfully to {1} in {2} s".format(
                self.date.strftime("%Y-%m-%d"), report_recipient.count(), elapsed_time)
            )
        )

