import time

from djangotrellostats.apps.dev_times.models import DailySpentTime
from djangotrellostats.apps.reporter.management.report_command import ReportCommand


class Command(ReportCommand):
    help = 'Monthly report for administrators'
    date_help_text = 'Send the monthly report to the administrators for the month this date belongs to'

    def handle(self, *args, **options):
        self.date = super(Command, self).handle(*args, **options)

        start = time.time()

        month = self.date.month
        year = self.date.year

        daily_spent_times = DailySpentTime.objects.filter(date__month=month, date__year=year).order_by("date", "member")

        subject = "[DjangoTrelloStats][Reports] Monthly report of {0}/{1}".format(year, month)
        txt_template_path = 'reporter/emails/monthly_report.txt'
        html_template_path = 'reporter/emails/monthly_report.html'
        csv_file_name = 'spent_times-for-month-{0}-{1}.csv'.format(year, month)

        administrator_users = self.send_reports(daily_spent_times, subject,
                                                txt_template_path, html_template_path, csv_file_name)
        self.stdout.write(
            self.style.SUCCESS(u"Monthly reports sent to {0} administrators".format(administrator_users.count())))

        end = time.time()
        elapsed_time = end - start

        self.stdout.write(
            self.style.SUCCESS(u"Monthly reports for month {0}/{1} sent successfully to {2} in {3} s".format(
                year, month, administrator_users.count(), elapsed_time)
            )
        )