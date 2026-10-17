# -*- coding: utf-8 -*-


from collections import OrderedDict

from django.db import models

from djanban.apps.boards.models import Card, List


# A multiboard is a board that references several boards and depends on a particular user
class Multiboard(models.Model):
    creator = models.ForeignKey(
        "members.Member",
        verbose_name="Member",
        related_name="created_multiboards",
        on_delete=models.CASCADE,
    )

    name = models.CharField(max_length=128, verbose_name="Name of the multiboard")

    description = models.TextField(
        max_length=128,
        verbose_name="Description of the multiboard",
        default="",
        blank=True,
    )

    is_archived = models.BooleanField(
        verbose_name="This multiboard is archived",
        help_text="Archived multiboards are not shown",
        default=False,
    )

    boards = models.ManyToManyField(
        "boards.Board", verbose_name="Boards", related_name="multiboards"
    )

    members = models.ManyToManyField(
        "members.Member", verbose_name="Members", related_name="multiboards", blank=True
    )

    order = models.PositiveIntegerField(
        verbose_name="Order of this multiboard", default=1
    )

    show_in_index = models.BooleanField(
        verbose_name="This multiboard will be shown in index",
        help_text="Multiboards shown in index will be show to help users track pending tasks",
        default=False,
    )

    show_backlog_tasks = models.BooleanField(
        verbose_name="Show 'backlog' tasks",
        help_text="This multiboard will show the backlog tasks of its boards",
        default=True,
    )

    show_ready_to_develop_tasks = models.BooleanField(
        verbose_name="Show 'ready to develop' tasks",
        help_text="This multiboard will show the 'ready to develop' tasks of its boards",
        default=True,
    )

    show_development_tasks = models.BooleanField(
        verbose_name="Show 'in development' tasks",
        help_text="This multiboard will show the in 'development' tasks of its boards",
        default=True,
    )

    show_after_development_in_review_tasks = models.BooleanField(
        verbose_name="Show 'after development (in review)' tasks",
        help_text="This multiboard will show the in 'after development (in review)' tasks of its boards",
        default=True,
    )

    show_after_development_waiting_release_tasks = models.BooleanField(
        verbose_name="Show 'after development (waiting release)' tasks",
        help_text="This multiboard will show the in 'after development (waiting release)' tasks of its boards",
        default=False,
    )

    show_done_tasks = models.BooleanField(
        verbose_name="Show 'done' tasks",
        help_text="This multiboard will show the done tasks of its boards",
        default=False,
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

    # Returns the spent times for this multiboard
    def get_spent_time(self, date=None, member=None):
        board_spent_time = 0
        for board_i in self.boards.all():
            board_spent_time += board_i._get_developed_time(
                attr="spent_time", date=date, member=member
            )
        return board_spent_time

    # Returns the adjusted spent time according to the spent time factor defined in each member for this multiboard
    def get_adjusted_spent_time(self, date=None, member=None):
        board_spent_time = 0
        for board_i in self.boards.all():
            board_spent_time += board_i._get_developed_time(
                attr="adjusted_spent_time", date=date, member=member
            )
        return board_spent_time

    # Return the tasks that belongs to this multiboard grouped by list types
    @property
    def tasks_by_list_type(self):
        tasks = OrderedDict()
        list_type_names = dict(List.LIST_TYPE_CHOICES)
        for list_type in self.active_list_types:
            multiboard_list_type_cards = Card.objects.filter(
                board__in=self.boards.filter(is_archived=False),
                list__type=list_type,
                is_closed=False,
            ).order_by("board", "position")
            tasks[list_type] = {
                "cards": multiboard_list_type_cards,
                "name": list_type_names[list_type],
            }
        return tasks
