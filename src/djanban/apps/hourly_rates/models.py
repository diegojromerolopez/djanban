# -*- coding: utf-8 -*-
from django.db import models


# Billing rate per hour
class HourlyRate(models.Model):

    class Meta:
        ordering = ["start_date", "end_date", "name"]

    creator = models.ForeignKey(
        "members.Member",
        verbose_name="Member",
        related_name="created_hourly_rates",
        on_delete=models.CASCADE,
    )

    name = models.CharField(verbose_name="Name for this hourly rate", max_length=128)

    start_date = models.DateField(
        verbose_name="Start date",
        help_text="Start date of application of this billing rate per hour",
    )

    end_date = models.DateField(
        verbose_name="End date",
        help_text="End date of application of this billing rate",
        blank=True,
        default=None,
        null=True,
    )

    amount = models.DecimalField(
        verbose_name="Amount billed per hour", decimal_places=4, max_digits=12
    )

    is_active = models.BooleanField(
        verbose_name="Should this billing rate should be applied?", default=True
    )

    def __str__(self):
        str_start_date = self.start_date.strftime("%Y-%m-%d")
        if self.end_date:
            str_end_date = self.end_date.strftime("%Y-%m-%d")
        else:
            str_end_date = "until now"
        return "{0} {1}¤ ({2} - {3})".format(
            self.name, self.amount, str_start_date, str_end_date
        )

    # def overlaps(self, hourly_rate):
    #     return (self.start_date >= hourly_rate.start_date and self.end_date >= hourly_rate.start_date)
