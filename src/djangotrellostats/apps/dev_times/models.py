# -*- coding: utf-8 -*-

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

    uuid = models.CharField(max_length=128, verbose_name=u"External id of the comment", unique=False, null=True)
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="daily_spent_times")
    card = models.ForeignKey("boards.Card", verbose_name=u"Card", related_name="daily_spent_times", null=True)
    comment = models.OneToOneField("boards.CardComment", verbose_name=u"Comment", related_name="daily_spent_time", null=True)
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

    @property
    def day(self):
        return self.date.day

    @property
    def month(self):
        return self.date.month

    @property
    def year(self):
        return self.date.year

    @property
    def iso_date(self):
        return self.date.isoformat()

    # Returns the adjusted spent time for this measurement
    def adjusted_spent_time(self):
        member = self.member
        return member.adjust_daily_spent_time(self, attribute="spent_time")

    # Add a new amount of spent time to a member
    @staticmethod
    def add_daily_spent_time(daily_spent_time):
        DailySpentTime.add(board=daily_spent_time.board,
                           card=daily_spent_time.card,
                           comment=daily_spent_time.comment,
                           description=daily_spent_time.description,
                           member=daily_spent_time.member,
                           date=daily_spent_time.date,
                           spent_time=daily_spent_time.spent_time,
                           estimated_time=daily_spent_time.estimated_time)

    # Add a new amount of spent time to a member
    @staticmethod
    def add(board, member, date, card, comment, description, spent_time, estimated_time):
        # In case a uuid is passed, load the Member object
        if type(member) is str or type(member) is unicode:
            try:
                member = board.members.get(uuid=member)
            except ObjectDoesNotExist:
                return False

        weekday = date.strftime("%w")
        week_of_year = get_iso_week_of_year(date)
        day_of_year = date.strftime("%j")

        # Convert spent_time to Decimal if is a number
        if spent_time is not None:
            spent_time = Decimal(spent_time)

        # Convert estimated_time to Decimal if is a number
        if estimated_time is not None:
            estimated_time = Decimal(estimated_time)
        elif spent_time is not None:
            estimated_time = Decimal(spent_time)

        # Compute difference between spent_time and estimated_time
        diff_time = None
        if spent_time is not None and estimated_time is not None:
            diff_time = Decimal(estimated_time) - Decimal(spent_time)

        # Creation of daily_spent_time
        daily_spent_time = DailySpentTime(board=board, member=member, card=card, comment=comment, uuid=comment.uuid,
                                          description=description,
                                          spent_time=spent_time,
                                          estimated_time=estimated_time,
                                          diff_time=diff_time,
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

    # Add a new amount of spent time to a member
    @staticmethod
    def factory_from_comment(comment):
        card = comment.card
        board = card.board
        spent_estimated_time = comment.get_spent_estimated_time_from_content()
        date = spent_estimated_time["date"]

        weekday = date.strftime("%w")
        week_of_year = get_iso_week_of_year(date)
        day_of_year = date.strftime("%j")

        spent_time = spent_estimated_time["spent_time"]
        estimated_time = spent_estimated_time["estimated_time"]

        if spent_time is not None:
            spent_time = Decimal(spent_time)

        # Convert estimated_time to Decimal if is a number
        if estimated_time is not None:
            estimated_time = Decimal(estimated_time)

        elif spent_time is not None:
            estimated_time = Decimal(spent_time)

        diff_time = estimated_time - spent_time

        rate_amount = None
        hourly_rate = board.get_date_hourly_rate(date)
        if spent_time is not None and hourly_rate is not None:
            rate_amount = spent_time * hourly_rate.amount

        daily_spent_time = DailySpentTime(
            uuid=comment.uuid, board=board, card=card, comment=comment,
            date=spent_estimated_time["date"], weekday=weekday, week_of_year=week_of_year, day_of_year=day_of_year,
            spent_time=spent_time, estimated_time=estimated_time, diff_time=diff_time,
            description=spent_estimated_time["description"],
            member=comment.author, rate_amount=rate_amount
        )
        return daily_spent_time

    @staticmethod
    def create_from_comment(comment):
        daily_spent_time = DailySpentTime.factory_from_comment(comment)
        if comment.id:
            daily_spent_time.save()
        else:
            daily_spent_time.comment = None
            daily_spent_time.save()
        return daily_spent_time

    # Set daily spent time from a card comment
    def set_from_comment(self, comment):
        spent_estimated_time = comment.spent_estimated_time
        if spent_estimated_time:
            self.date = spent_estimated_time["date"]
            self.spent_time = spent_estimated_time["spent_time"]
            self.estimated_time = spent_estimated_time["estimated_time"]