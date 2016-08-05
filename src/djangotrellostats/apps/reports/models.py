from __future__ import unicode_literals

from django.db import models


# Stat report by list
class ListReport(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="list_reports", null=True)
    list = models.OneToOneField("boards.List", verbose_name=u"List", related_name="list_reports", unique=True)
    forward_movements = models.PositiveIntegerField(verbose_name=u"Forward movements")
    backward_movements = models.PositiveIntegerField(verbose_name=u"Backward movements")
    avg_card_time = models.DecimalField(verbose_name=u"Average time cards live in this list", decimal_places=4,
                                        max_digits=12, default=None, null=True)
    std_dev_card_time = models.DecimalField(verbose_name=u"Average time cards live in this list", decimal_places=4,
                                            max_digits=12, default=None, null=True)


# Stat report by member
class MemberReport(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="member_reports")
    number_of_cards = models.PositiveIntegerField(verbose_name=u"Number of assigned cards", default=0)
    member = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="member_reports")
    forward_movements = models.PositiveIntegerField(verbose_name=u"Forward movements")
    backward_movements = models.PositiveIntegerField(verbose_name=u"Backward movements")
    avg_card_time = models.DecimalField(verbose_name=u"Average time a card lives in the board", decimal_places=4,
                                        max_digits=12, default=None, null=True)
    std_dev_card_time = models.DecimalField(verbose_name=u"Std. Dev. time a card lives in the board", decimal_places=4,
                                            max_digits=12, default=None, null=True)
    avg_card_spent_time = models.DecimalField(verbose_name=u"Average card spent time", decimal_places=4, max_digits=12,
                                              default=None, null=True)
    std_dev_card_spent_time = models.DecimalField(verbose_name=u"Std. Deviation card spent time", decimal_places=4,
                                                  max_digits=12,
                                                  default=None, null=True)
    avg_card_estimated_time = models.DecimalField(verbose_name=u"Average task estimated card completion time",
                                                  decimal_places=4,
                                                  max_digits=12, default=None, null=True)
    std_dev_card_estimated_time = models.DecimalField(verbose_name=u"Std. Deviation of the estimated card completion time",
                                                      decimal_places=4,
                                                      max_digits=12, default=None, null=True)

