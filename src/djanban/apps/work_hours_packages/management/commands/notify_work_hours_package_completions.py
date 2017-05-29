# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from decimal import Decimal
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.template.loader import get_template
from django.utils import timezone

from djanban.apps.work_hours_packages.models import WorkHoursPackage


# Notification completion email send
class Command(BaseCommand):
    help = u'Notify if any work hours package has been completed'

    def __init__(self, stdout=None, stderr=None, no_color=False, member=None):
        super(Command, self).__init__(stdout, stderr, no_color)
        self.member = member

    # Handle de command action
    def handle(self, *args, **options):
        today = timezone.now().date()
        candidate_to_completion_packages = WorkHoursPackage.objects.filter(
                Q(half_completion_notification_datetime__isnull=True)|
                Q(eighty_percent_completion_notification_datetime__isnull=True)|
                Q(ninety_percent_completion_notification_datetime__isnull=True)|
                Q(completion_notification_datetime__isnull=True)|
                (Q(end_work_date__isnull=True) | Q(end_work_date__lte=today)),
                start_work_date__lte=today,
                notify_on_completion=True
        )
        # In case we are calling this command from the web app, a filter by member is needed
        if self.member:
            candidate_to_completion_packages = candidate_to_completion_packages.filter(members__in=self.member)

        # Notifications send
        number_of_sent_notifications = 0
        for package in candidate_to_completion_packages:
            adjusted_time = package.get_adjusted_spent_time()
            percentage = None
            # Selection of percentage, not the best code but it works
            if package.completion_notification_datetime is None and\
                    adjusted_time >= package.number_of_hours:
                percentage = "100%"
            elif package.ninety_percent_completion_notification_datetime is None and\
                    adjusted_time >= package.number_of_hours * Decimal(0.9):
                percentage = "90%"
            elif package.eighty_percent_completion_notification_datetime is None and\
                    adjusted_time >= package.number_of_hours * Decimal(0.8):
                percentage = "80%"
            elif package.half_completion_notification_datetime is None and\
                    adjusted_time >= package.number_of_hours * Decimal(0.5):
                percentage = "50%"

            # If it is in one of the percentages we have defined, send the emails
            if percentage:
                self.send_package_notification(package, percentage)
                self.stdout.write(
                    self.style.SUCCESS(u"Notifications for {0} of {1} sent successfully".format(percentage, package.full_name))
                )
                number_of_sent_notifications += 1

            self.stdout.write(
                self.style.SUCCESS(
                    u"{0} notification(s) sent successfully".format(number_of_sent_notifications))
            )

    def send_package_notification(self, package, percentage):
        # Recipient emails
        # Deletion of repeated emails using a hash
        emails = {member.user.email:True for member in package.members.exclude(user__email="")}
        if package.notification_email:
            emails[package.notification_email] = True
        emails = emails.keys()

        daily_spent_times = package.daily_spent_times

        # Preparation of email templates
        replacements = {
            "work_hours_package": package,
            "completion_datetime": package.completion_date,
            "daily_spent_times": daily_spent_times,
            "percentage": percentage
        }
        txt_message = get_template('work_hours_packages/emails/completion_notification.txt')\
            .render(replacements)
        html_message = get_template('work_hours_packages/emails/completion_notification.html')\
            .render(replacements)

        subject = "[Djanban][WorkHoursPackage] Work hours package {0} at {1}".format(package.name, percentage)

        csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})

        try:
            # Send the email
            message = EmailMultiAlternatives(subject, txt_message, settings.EMAIL_HOST_USER,
                                             bcc=emails)
            message.attach_alternative(html_message, "text/html")
            message.attach('spent_times-for-{0}.csv'.format(package.name), csv_report, 'text/csv')
            message.send()
            # Mark this work hours package as notified
            package.mark_completion_notification_as_sent(percentage)
        except Exception:
            self.stdout.write(
                self.style.ERROR(u"Notifications of {0} could not be sent successfully".format(package.name))
            )


