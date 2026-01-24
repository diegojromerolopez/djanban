# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from djanban.apps.boards.forms import NewBoardForm, EditBoardForm
from djanban.apps.boards.models import Board, List
from djanban.apps.members.models import Member, MemberRole


# Test for board application
class BoardTest(TestCase):

    # Creates an empty database without a backend
    def setUp(self):
        user = get_user_model().objects.create_user('test')
        self.member = Member.objects.create(user=user, is_developer=True)

    # Test the creation of a new board
    def test_create_board(self):
        form_data = {"name": "New test board", "description": "description of board"}
        new_board_form = NewBoardForm(data=form_data, member=self.member)
        self.assertTrue(new_board_form.is_valid())
        new_board = new_board_form.save(commit=True)
        # Checking name and description of the board
        self.assertEqual(new_board.name, form_data["name"], "Board names do not match")
        self.assertEqual(new_board.description, form_data["description"], "Board descriptions do not match")
        # Testing if creator is our current member
        self.assertEqual(new_board.creator, self.member, "Board creator is not right")
        # Testing if creator is also a member of the board
        self.assertTrue(
            new_board.members.filter(id=self.member.id).exists(), "Member creator is not a member of the board"
        )
        # Testing if creator is admin
        member_role_for_new_board = MemberRole.objects.get(board=new_board, type="admin")
        self.assertTrue(member_role_for_new_board.members.filter(id=self.member.id).exists(),
                        "Member creator ha not the admin role")

    # Test edition of a board
    def test_edit_board(self):
        """Test edition of a list for this board"""
        board = Board.objects.create(
            creator=self.member, name="Board name", description="board description", comments="board comments"
        )
        form_data = {
                        "has_to_be_fetched": False,
                        "comments": "This are the comments of the board",
                        "estimated_number_of_hours": 400,
                        "percentage_of_completion": 80,
                        "hourly_rates": [],
                        "enable_public_access": True,
                        "public_access_code": "ZZZ",
                        "show_on_slideshow": True,
                        "background_color": "CCCCC",
                        "title_color": "BBBBB",
                        "header_image": None
        }
        edit_board_form = EditBoardForm(data=form_data, instance=board)
        self.assertTrue(edit_board_form.is_valid())

        edited_board = edit_board_form.save(commit=True)
        for field, value in form_data.items():
            if field != "hourly_rates" and field != "header_image":
                self.assertEqual(getattr(edited_board, field), value, "Attribute {0} does not match".format(field))

