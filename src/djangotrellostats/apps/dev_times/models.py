from __future__ import unicode_literals

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from djangotrellostats.utils.week import get_iso_week_of_year


# Daily spent time by member
class DailySpentTime(models.Model):

    class Meta:
        verbose_name = u"Spent time"
        verbose_name_plural = u"Spent times"
        index_together = (
            ("date", "week_of_year", "spent_time"),
            ("date", "week_of_year", "board", "spent_time"),
            ("board", "date", "week_of_year", "spent_time")
        )

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="daily_spent_times")
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="daily_spent_times", null=True)
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="daily_spent_times")
    description = models.TextField(verbose_name="Description of the task")
    date = models.DateField(verbose_name="Date of the time measurement")
    day_of_year = models.CharField(verbose_name="Day number of the time measurement", max_length=16)
    week_of_year = models.CharField(verbose_name="Week number of the time measurement", max_length=16)
    weekday = models.CharField(verbose_name="Week day of the time measurement", max_length=16)

    spent_time = models.DecimalField(verbose_name=u"Spent time for this day", decimal_places=4, max_digits=12,
                                     default=None, null=True)

    rate_amount = models.DecimalField(verbose_name=u"Rate amount for this spent time", decimal_places=4, max_digits=12,
                                      default=None, null=True)

    estimated_time = models.DecimalField(verbose_name=u"Estimated time for this day", decimal_places=4, max_digits=12,
                                         default=None, null=True)

    diff_time = models.DecimalField(verbose_name=u"Difference between the estimated time and the spent time",
                                    decimal_places=4, max_digits=12,
                                    default=None, null=True)

    # Add a new amount of spent time to a member
    @staticmethod
    def add_daily_spent_time(daily_spent_time):
        DailySpentTime.add(board=daily_spent_time.board,
                           card=daily_spent_time.card,
                           description=daily_spent_time.description,
                           member=daily_spent_time.member,
                           date=daily_spent_time.date,
                           spent_time=daily_spent_time.spent_time,
                           estimated_time=daily_spent_time.estimated_time)

    # Add a new amount of spent time to a member
    @staticmethod
    def add(board, member, date, card, description, spent_time, estimated_time):
        # In case a uuid is passed, load the Member object
        if type(member) is str or type(member) is unicode:
            try:
                member = board.members.get(uuid=member)
            except ObjectDoesNotExist:
                return False

        weekday = date.strftime("%w")
        week_of_year = get_iso_week_of_year(date)
        day_of_year = date.strftime("%j")
        daily_spent_time = DailySpentTime(board=board, member=member, card=card,
                                          description=description,
                                          spent_time=Decimal(spent_time),
                                          estimated_time=Decimal(estimated_time),
                                          diff_time=Decimal(estimated_time) - Decimal(spent_time),
                                          date=date, day_of_year=day_of_year, week_of_year=week_of_year,
                                          weekday=weekday)

        # Rate amount computation
        hourly_rate = board.get_date_hourly_rate(date)
        if hourly_rate:
            if daily_spent_time.rate_amount is None:
                daily_spent_time.rate_amount = 0
            daily_spent_time.rate_amount += hourly_rate.amount

        # Saving the daily spent time
        daily_spent_time.save()
        return spent_time

