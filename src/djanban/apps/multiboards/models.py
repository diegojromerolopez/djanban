# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from djanban.apps.boards.models import List, Card
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

    members = models.ManyToManyField("members.Member", verbose_name=u"Members", related_name="multiboards")

    order = models.PositiveIntegerField(verbose_name=u"Order of this multiboard", default=1)

    show_in_index = models.BooleanField(
        verbose_name=u"This multiboard will be shown in index",
        help_text=u"Multiboards shown in index will be show to help users track pending tasks",
        default=False
    )

    show_backlog_tasks = models.BooleanField(
        verbose_name=u"Show 'backlog' tasks",
        help_text=u"This multiboard will show the backlog tasks of its boards",
        default=True
    )

    show_ready_to_develop_tasks = models.BooleanField(
        verbose_name=u"Show 'ready to develop' tasks",
        help_text=u"This multiboard will show the 'ready to develop' tasks of its boards",
        default=True
    )

    show_development_tasks = models.BooleanField(
        verbose_name=u"Show 'in development' tasks",
        help_text=u"This multiboard will show the in 'development' tasks of its boards",
        default=True
    )

    show_after_development_in_review_tasks = models.BooleanField(
        verbose_name=u"Show 'after development (in review)' tasks",
        help_text=u"This multiboard will show the in 'after development (in review)' tasks of its boards",
        default=True
    )

    show_after_development_waiting_release_tasks = models.BooleanField(
        verbose_name=u"Show 'after development (waiting release)' tasks",
        help_text=u"This multiboard will show the in 'after development (waiting release)' tasks of its boards",
        default=False
    )

    show_done_tasks = models.BooleanField(
        verbose_name=u"Show 'done' tasks",
        help_text=u"This multiboard will show the done tasks of its boards",
        default=False
    )

    # Return a list with the active list types in this multiboard
    @property
    def active_list_types(self):
        active_list_types = []
        if self.show_backlog_tasks:
            active_list_types.append("backlog")
        if self.show_ready_to_develop_tasks:
            active_list_types.append("ready_to_develop")
        if self.show_development_tasks:
            active_list_types.append("development")
        if self.show_after_development_in_review_tasks:
            active_list_types.append("after_development_in_review")
        if self.show_after_development_waiting_release_tasks:
            active_list_types.append("after_development_waiting_release")
        if self.show_done_tasks:
            active_list_types.append("done")
        return active_list_types

    # Return the tasks that belongs to this multiboard grouped by list types
    @property
    def tasks_by_list_type(self):
        tasks = OrderedDict()
        list_type_names = dict(List.LIST_TYPE_CHOICES)
        for list_type in self.active_list_types:
            multiboard_list_type_cards = Card.objects.filter(
                board__in=self.boards.filter(is_archived=False),
                list__type=list_type,
                is_closed=False
            ).order_by("board", "position")
            tasks[list_type] = {"cards": multiboard_list_type_cards, "name": list_type_names[list_type]}
        return tasks
