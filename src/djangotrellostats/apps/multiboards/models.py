# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from djangotrellostats.apps.boards.models import List, Card
from collections import OrderedDict


# A multiboard is a board that references several boards and depends on a particular user
class Multiboard(models.Model):
    creator = models.ForeignKey("members.Member", verbose_name=u"Member", related_name="created_multiboards")

    name = models.CharField(max_length=128, verbose_name=u"Name of the multiboard")

    description = models.TextField(max_length=128, verbose_name=u"Description of the multiboard", default="", blank=True)

    is_archived = models.BooleanField(
        verbose_name=u"This multiboard is archived",
        help_text=u"Archived multiboards are not shown",
        default=False
    )

    boards = models.ManyToManyField("boards.Board", verbose_name=u"Boards", related_name="multiboards")

    order = models.PositiveIntegerField(verbose_name=u"Order of this multiboard", default=1)

    # Return the tasks that belongs to this multiboard grouped by list types
    @property
    def tasks_by_list_type(self):
        tasks = OrderedDict()
        list_type_names = dict(List.LIST_TYPE_CHOICES)
        for list_type in List.ACTIVE_LIST_TYPES:
            multiboard_list_type_cards = Card.objects.filter(
                board__in=self.boards.filter(is_archived=False),
                list__type=list_type,
                is_closed=False
            ).order_by("board", "position")
            tasks[list_type] = {"cards": multiboard_list_type_cards, "name": list_type_names[list_type]}
        return tasks
