# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

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
                Q(end_work_date__isnull=True) | Q(end_work_date__lte=today), start_work_date__lte=today,
                notify_on_completion=True,
                completion_notification_datetime__isnull=True
        )
        # In case we are calling this command from the web app, a filter by member is needed
        if self.member:
            candidate_to_completion_packages = candidate_to_completion_packages.filter(members__in=self.member)

        # Notification send
        number_of_sent_notifications = 0
        for package in candidate_to_completion_packages:
            package_completion_date = package.completion_date
            if package_completion_date:
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
                    "completion_datetime": package_completion_date,
                    "daily_spent_times": daily_spent_times
                }
                txt_message = get_template('work_hours_packages/emails/completion_notification.txt')\
                    .render(replacements)
                html_message = get_template('work_hours_packages/emails/completion_notification.html')\
                    .render(replacements)

                subject = "[Djanban][WorkHoursPackage] Work hours package {0} completed".format(package.name)

                csv_report = get_template('daily_spent_times/csv.txt').render({"spent_times": daily_spent_times})

                try:
                    # Send the email
                    message = EmailMultiAlternatives(subject, txt_message, settings.EMAIL_HOST_USER,
                                                     bcc=emails)
                    message.attach_alternative(html_message, "text/html")
                    message.attach('spent_times-for-{0}.csv'.format(package.name), csv_report, 'text/csv')
                    message.send()
                    # Mark this work hours package as notified
                    package.mark_completion_notification_as_sent()
                except Exception:
                    self.stdout.write(
                        self.style.ERROR(u"Notifications of {0} could not be sent successfully".format(package.name))
                    )

                self.stdout.write(
                    self.style.SUCCESS(u"Notifications for {0} sent successfully".format(package.full_name))
                )
                number_of_sent_notifications += 1

            self.stdout.write(
                self.style.SUCCESS(u"{0} notification(s) sent successfully".format(number_of_sent_notifications))
            )
