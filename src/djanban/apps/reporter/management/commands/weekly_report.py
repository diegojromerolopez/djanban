import time

from isoweek import Week

from djanban.apps.dev_times.models import DailySpentTime
from djanban.apps.reporter.management.report_command import ReportCommand
from djanban.utils.week import get_iso_week_of_year


class Command(ReportCommand):
    help = "Weekly report for administrators"

    def handle(self, *args, **options):
        self.date = super().handle(*args, **options)
        date_help_text = "Send the weekly report to the administrators for the week this date belongs to"

        start = time.time()

        week = get_iso_week_of_year(self.date)
        year = self.date.year

        week_start_date = Week(year, week).monday()
        week_end_date = Week(year, week).friday()

        daily_spent_times = DailySpentTime.objects.filter(
            date__gte=week_start_date, date__lte=week_end_date
        ).order_by("date", "member")

        subject = f"[Djanban][Reports] Weekly report of {year}/W{week}"
        txt_template_path = "reporter/emails/weekly_report.txt"
        html_template_path = "reporter/emails/weekly_report.html"
        csv_file_name = f"spent_times-for-month-{year}W{week}.csv"

        report_recipient = self.send_reports(
            daily_spent_times,
            subject,
            txt_template_path,
            html_template_path,
            csv_file_name,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Weekly reports sent to {report_recipient.count()} administrators"
            )
        )

        end = time.time()
        elapsed_time = end - start

        self.stdout.write(
            self.style.SUCCESS(
                "Weekly reports for week {}/W{} sent successfully to {} in {} s".format(
                    year, week, report_recipient.count(), elapsed_time
                )
            )
        )
