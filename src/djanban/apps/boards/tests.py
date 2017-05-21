# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from djanban.apps.boards.forms import NewListForm, SwapListForm, MoveUpListForm
from djanban.apps.boards.models import Board, List
from djanban.apps.members.models import Member


class BoardTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user('test')
        self.member = Member.objects.create(user=user, is_developer=True)
        self.board = Board.objects.create(
            creator=self.member, name="Board name", description="board description", comments="board comments"
        )

        self.lists = []
        # Create some lists, one for each type of active list
        for list_type in List.ACTIVE_LIST_TYPES:
            form_data = {"name": "{0} list".format(list_type), "type": list_type}
            form = NewListForm(data=form_data, instance=List(board=self.board), member=self.member)
            self.assertTrue(form.is_valid())
            list_i = form.save(commit=True)
            self.lists.append(list_i)

    def test_new_list_form(self):
        """Test list creation for this board"""

        # Create a new "backlog" list
        form_data = {"name": "Proposals", "type": "backlog", "wip_limit": 5}
        new_list_form = NewListForm(data=form_data, instance=List(board=self.board), member=self.member)
        self.assertTrue(new_list_form.is_valid())
        new_list = new_list_form.save(commit=True)
        self.assertEqual(new_list.name, "Proposals", "List names do not match")
        self.assertEqual(new_list.type, "backlog", "List types do not match")
        self.assertEqual(new_list.wip_limit, 5, "WIP limits do not match")

        # Move the new list up 6 times to be the first list
        for list_type in List.ACTIVE_LIST_TYPES:
            move_up_form = MoveUpListForm(data={"movement_type": "up"}, instance=new_list, member=self.member)
            self.assertTrue(move_up_form.is_valid())
            move_up_form.save()
        self.assertTrue(new_list.is_first)
