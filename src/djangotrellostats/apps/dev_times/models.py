from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from decimal import Decimal


# Daily spent time by member
class DailySpentTime(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="daily_spent_times")
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="daily_spent_times")

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
                           member=daily_spent_time.member,
                           date=daily_spent_time.date,
                           spent_time=daily_spent_time.spent_time,
                           estimated_time=daily_spent_time.estimated_time)

    # Add a new amount of spent time to a member
    @staticmethod
    def add(board, member, date, spent_time, estimated_time):
        # In case a uuid is passed, load the Member object
        if type(member) is str or type(member) is unicode:
            try:
                member = board.members.get(uuid=member)
            except ObjectDoesNotExist:
                return False

        # Add the spent time value to the total amount of time this member has spent
        try:
            daily_spent_time = DailySpentTime.objects.get(board=board, member=member, date=date)
            if daily_spent_time.spent_time is None:
                daily_spent_time.spent_time = Decimal("0.0")
            daily_spent_time.spent_time += Decimal(spent_time)
            if daily_spent_time.estimated_time is None:
                daily_spent_time.estimated_time = Decimal("0.0")
            daily_spent_time.estimated_time += Decimal(estimated_time)
            daily_spent_time.diff_time += (Decimal(estimated_time) - Decimal(spent_time))

        except DailySpentTime.DoesNotExist:
            weekday = date.strftime("%w")
            week_of_year = DailySpentTime.get_iso_week_of_year(date)
            day_of_year = date.strftime("%j")
            daily_spent_time = DailySpentTime(board=board, member=member,
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

    @staticmethod
    def get_iso_week_of_year(date):
        iso_calendar_date = date.isocalendar()
        week_of_year = iso_calendar_date[1]
        return week_of_year
