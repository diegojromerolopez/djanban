# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from djanban.apps.dev_times.models import DailySpentTime


# A package of work hours: support, development or whatever type of work a client needs.
class WorkHoursPackage(models.Model):

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="work_hours_packages", null=True, default=None, blank=True)
    multiboard = models.ForeignKey("multiboards.Multiboard", verbose_name=u"Multiboard", related_name="work_hours_packages", null=True, default=None, blank=True)
    label = models.ForeignKey("boards.Label", verbose_name=u"Label", related_name="work_hours_packages", null=True, default=None, blank=True)

    name = models.CharField(max_length=256, verbose_name=u"Name of this package")

    offset_hours = models.DecimalField(
        verbose_name=u"Offset hours",
        help_text=u"This hours will be added as an initial offset of the spent time measurements "
                  u"gotten in the date interval",
        default=0, blank=True,
        decimal_places=2, max_digits=10
    )
    offset_hours_description = models.TextField(
        verbose_name="Offset hours description",
        help_text=u"Provide a description of the tasks that were done in this hours",
        default="", blank=True
    )

    notify_on_completion = models.BooleanField(verbose_name=u"Notify the members and this email on completion", default=False, blank=True)
    notification_email = models.EmailField(verbose_name=u"Notification email when number of hours is reached", default="", blank=True)
    completion_notification_datetime = models.DateTimeField(verbose_name=u"Notification was sent in this date and time", default=None, null=True, blank=True)

    description = models.TextField(
        verbose_name=u"Description of this package",
        help_text=u"Long description of this pakage describing the"
                  u"type of work the workers must do"
    )

    number_of_hours = models.DecimalField(
        verbose_name=u"Number of hours",
        help_text=u"Number of hours of this package.",
        decimal_places=2, max_digits=10
    )

    is_paid = models.BooleanField(verbose_name=u"Is this package paid?",
                                  help_text="Has the client paid for this package", default=False)

    payment_date = models.DateField(verbose_name=u"When this package was paid", default=None, null=True, blank=True)

    start_work_date = models.DateField(verbose_name=u"Start date")
    end_work_date = models.DateField(verbose_name=u"End date")

    creator = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="created_work_hours_packages")
    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="work_hours_packages", blank=True)

    @property
    def full_name(self):
        if self.start_work_date and self.end_work_date:
            return "{0} {1}-{2}".format(self.name, self.start_work_date, self.end_work_date)
        elif self.start_work_date:
            return "{0} {1}".format(self.name, self.start_work_date)
        return "{0}".format(self.name)

    @property
    def type(self):
        if self.multiboard:
            return "multiboard"
        if self.board:
            return "board"
        if self.label:
            return "label"
        raise ValueError("This work hours package is not defined for a (multi)board or label")

    def get_spent_time(self):
        date_interval = (self.start_work_date, self.end_work_date)
        if self.board:
            return self.board.spent_number_of_hours(date=date_interval)
        if self.label:
            return self.label.spent_number_of_hours(date=date_interval)
        if self.multiboard:
            return self.multiboard.spent_number_of_hours(date=date_interval)
        raise ValueError("This work hours package is not defined for a (multi)board or label")

    def get_adjusted_spent_time(self):
        date_interval = (self.start_work_date, self.end_work_date)
        if self.board:
            return self.board.get_adjusted_spent_time(date=date_interval)
        if self.label:
            return self.label.get_adjusted_spent_time(date=date_interval)
        if self.multiboard:
            return self.multiboard.get_adjusted_spent_time(date=date_interval)
        raise ValueError("This work hours package is not defined for a (multi)board or label")

    # Get the daily spent times associated with this work hour package
    @property
    def daily_spent_times(self):
        daily_spent_time_filter = {"date__gte": self.start_work_date}
        if self.end_work_date:
            daily_spent_time_filter["date__lte"] = self.end_work_date
        if self.board:
            daily_spent_time_filter["board"] = self.board
        elif self.multiboard:
            daily_spent_time_filter["board__in"] = [board.id for board in self.multiboard.boards.all()]
        elif self.label:
            daily_spent_time_filter["board"] = self.label.board
            daily_spent_time_filter["card__labels"] = self.label
        daily_spent_times = DailySpentTime.objects.filter(**daily_spent_time_filter)
        return daily_spent_times

    # Get the date of the last spent time measurement
    @property
    def completion_date(self):
        last_daily_spent_time_in_this_work_package = self.last_daily_spent_time
        if last_daily_spent_time_in_this_work_package:
            return last_daily_spent_time_in_this_work_package.date
        return None

    # Get the last spent time measurement
    @property
    def last_daily_spent_time(self):
        # In case this package has not been spent, there is not last daily spent time
        adjusted_time = self.get_adjusted_spent_time()
        if adjusted_time < self.number_of_hours:
            return None
        # Otherwise, get the last daily spent time measurement date of the measurements that
        # belong to the package interval
        try:
            return self.daily_spent_times.order_by("-date")[0]
        except IndexError:
            return None

    # Mark this work hours package completion notification as sent to its members
    def mark_completion_notification_as_sent(self):
        self.completion_notification_datetime = timezone.now()
        self.save()
