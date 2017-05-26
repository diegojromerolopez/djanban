# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# A package of work hours: support, development or whatever type of work a client needs.
class WorkHoursPackage(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="work_hours_packages", null=True, default=None, blank=True)
    multiboard = models.ForeignKey("multiboards.Multiboard", verbose_name=u"Multiboard", related_name="work_hours_packages", null=True, default=None, blank=True)
    label = models.ForeignKey("boards.Label", verbose_name=u"Label", related_name="work_hours_packages", null=True, default=None, blank=True)

    name = models.CharField(max_length=256, verbose_name=u"Name of this package")

    notification_email = models.EmailField(verbose_name=u"Notification email when number of hours is reached", default="", blank=True)

    description = models.TextField(
        verbose_name=u"Description of this package",
        help_text=u"Long description of this pakage describing the"
                  u"type of work the workers must do"
    )

    number_of_hours = models.PositiveIntegerField(
        verbose_name=u"Number of hours",
        help_text=u"Number of hours of this package."
    )

    is_paid = models.BooleanField(verbose_name=u"Is this package paid?",
                                  help_text="Has the client paid for this package", default=False)

    payment_date = models.DateField(verbose_name=u"When this package was paid", default=None, null=True, blank=True)

    start_work_date = models.DateField(verbose_name=u"Start date")
    end_work_date = models.DateField(verbose_name=u"End date")

    creator = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="created_work_hours_packages")
    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="work_hours_packages", blank=True)

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
