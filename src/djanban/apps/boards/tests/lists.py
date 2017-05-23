# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from djanban.apps.boards.forms import NewListForm, SwapListForm, MoveUpListForm, EditListForm, MoveDownListForm
from djanban.apps.boards.models import Board, List
from djanban.apps.members.models import Member


# Test for lists in board application
class ListTest(TestCase):

    # Creates an empty database without a backend
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

    # Test creation of list
    def test_create_list(self):
        """Test list creation for this board"""
        # Create a new "backlog" list
        form_data = {"name": "ProposalsX", "type": "backlog", "wip_limit": 5}
        new_list_form = NewListForm(data=form_data, instance=List(board=self.board), member=self.member)
        self.assertTrue(new_list_form.is_valid())
        new_list = new_list_form.save(commit=True)
        self.assertEqual(new_list.name, "ProposalsX", "List names do not match")
        self.assertEqual(new_list.type, "backlog", "List types do not match")
        self.assertEqual(new_list.wip_limit, 5, "WIP limits do not match")

    # Test edition of list
    def test_edit_list(self):
        # Edit "backlog" list
        form_data = {"name": "Proposals", "type": "backlog", "wip_limit": None}
        edit_list_form = EditListForm(data=form_data, instance=self.lists[0])
        self.assertTrue(edit_list_form.is_valid())
        edited_list = edit_list_form.save(commit=True)
        self.assertEqual(edited_list.name, "Proposals", "List names do not match")
        self.assertEqual(edited_list.type, "backlog", "List types do not match")
        self.assertEqual(edited_list.wip_limit, None, "WIP limits do not match")

    # Test movement of list
    def test_move_list(self):
        # New lists are created at last lists
        form_data = {"name": "Last list", "type": "backlog", "wip_limit": 5}
        new_list_form = NewListForm(data=form_data, instance=List(board=self.board), member=self.member)
        self.assertTrue(new_list_form.is_valid(), "Last list is not valid")
        new_list = new_list_form.save(commit=True)

        # Move the new list up 6 times to be the first list
        for list_type in List.ACTIVE_LIST_TYPES:
            move_up_form = MoveUpListForm(data={"movement_type": "up"}, instance=new_list, member=self.member)
            self.assertTrue(move_up_form.is_valid())
            move_up_form.save()
        self.assertTrue(new_list.is_first, "List should be the first one (was moved up to the first position)")

        # Move the new list down 6 times to be the last list
        for list_type in List.ACTIVE_LIST_TYPES:
            move_down_form = MoveDownListForm(data={"movement_type": "down"}, instance=new_list, member=self.member)
            self.assertTrue(move_down_form.is_valid())
            move_down_form.save()
        self.assertTrue(new_list.is_last, "List should be the last one (was moved down to the last position)")

    # Swap of two lists
    def test_swap_list(self):
        # New lists are created at last lists
        new_list_form_data = {"name": "Last list", "type": "backlog", "wip_limit": 5}
        new_list_form = NewListForm(data=new_list_form_data, instance=List(board=self.board), member=self.member)
        self.assertTrue(new_list_form.is_valid(), "Last list is not valid")
        new_list = new_list_form.save(commit=True)
        # Swap this new list with the first one
        swap_form_data = {"list_to_be_swapped_with": self.lists[0].id}
        swap_list_form = SwapListForm(data=swap_form_data, instance=new_list, member=self.member)
        self.assertTrue(swap_list_form.is_valid())
        swap_list_form.save()
        self.assertTrue(
            new_list.is_first,
            "New list should be the first one (was swapped with the earlier first one list)"
        )
