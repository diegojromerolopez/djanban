from __future__ import unicode_literals

from django.db import models
from decimal import Decimal


# Create your models here.
# Daily spent time by member
class DailySpentTime(models.Model):
    fetch = models.ForeignKey("boards.Fetch", verbose_name=u"Fetch", related_name="daily_spent_times")
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="daily_spent_times")
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="daily_spent_times")

    date = models.DateField(verbose_name="Date of the time measurement")
    day_of_year = models.CharField(verbose_name="Day number of the time measurement", max_length=16)
    week_of_year = models.CharField(verbose_name="Week number of the time measurement", max_length=16)
    weekday = models.CharField(verbose_name="Week day of the time measurement", max_length=16)

    spent_time = models.DecimalField(verbose_name=u"Spent time for this day", decimal_places=4, max_digits=12,
                                     default=None, null=True)

    estimated_time = models.DecimalField(verbose_name=u"Estimated time for this day", decimal_places=4, max_digits=12,
                                         default=None, null=True)

    diff_time = models.DecimalField(verbose_name=u"Difference between the estimated time and the spent time",
                                    decimal_places=4, max_digits=12,
                                    default=None, null=True)

    # Add a new amount of spent time to a member
    @staticmethod
    def add(fetch, board, member, date, spent_time, estimated_time):
        # In case a uuid is passed, load the Member object
        if type(member) is str or type(member) is unicode:
            member = board.members.get(uuid=member)

        # Add the spent time value to the total amount of time this member has spent
        try:
            daily_spent_time = DailySpentTime.objects.get(fetch=fetch, board=board, member=member, date=date)
            daily_spent_time.spent_time += Decimal(spent_time)
            daily_spent_time.estimated_time += Decimal(estimated_time)
            daily_spent_time.diff_time += (Decimal(estimated_time) - Decimal(spent_time))

        except DailySpentTime.DoesNotExist:
            iso_calendar_date = date.isocalendar()
            weekday = date.strftime("%w")
            week_of_year = iso_calendar_date[1]
            day_of_year = date.strftime("%j")
            daily_spent_time = DailySpentTime(fetch=fetch, board=board, member=member,
                                              spent_time=Decimal(spent_time),
                                              estimated_time=Decimal(estimated_time),
                                              diff_time=Decimal(estimated_time) - Decimal(spent_time),
                                              date=date, day_of_year=day_of_year, week_of_year=week_of_year,
                                              weekday=weekday)

        daily_spent_time.save()
        return spent_time
