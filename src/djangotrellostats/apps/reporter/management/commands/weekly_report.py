from __future__ import unicode_literals

import time

from isoweek import Week

from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.reporter.management.report_command import ReportCommand
from djangotrellostats.utils.week import get_iso_week_of_year


class Command(ReportCommand):
    help = 'Weekly report for administrators'

    def handle(self, *args, **options):
        self.date = super(Command, self).handle(*args, **options)
        date_help_text = 'Send the weekly report to the administrators for the week this date belongs to'

        start = time.time()

        week = get_iso_week_of_year(self.date)
        year = self.date.year

        week_start_date = Week(year, week).monday()
        week_end_date = Week(year, week).friday()

        daily_spent_times = DailySpentTime.objects.filter(date__gte=week_start_date, date__lte=week_end_date).\
            order_by("date", "member")

        subject = "[DjangoTrelloStats][Reports] Weekly report of {0}/W{1}".format(year, week)
        txt_template_path = 'reporter/emails/weekly_report.txt'
        html_template_path = 'reporter/emails/weekly_report.html'
        csv_file_name = 'spent_times-for-month-{0}W{1}.csv'.format(year, week)

        report_recipient = self.send_reports(daily_spent_times, subject,
                                                txt_template_path, html_template_path, csv_file_name)
        self.stdout.write(
            self.style.SUCCESS(u"Weekly reports sent to {0} administrators".format(report_recipient.count())))

        end = time.time()
        elapsed_time = end - start

        self.stdout.write(
            self.style.SUCCESS(u"Weekly reports for week {0}/W{1} sent successfully to {2} in {3} s".format(
                year, week, report_recipient.count(), elapsed_time)
            )
        )