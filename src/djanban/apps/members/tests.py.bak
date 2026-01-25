# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.contrib.auth import get_user_model
from djanban.apps.members.models import Member, TrelloMemberProfile

class MemberTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='password'
        )

    def test_create_member(self):
        member = Member.objects.create(user=self.user, is_developer=True)
        self.assertEqual(member.user, self.user)
        self.assertTrue(member.is_developer)
        self.assertEqual(member.initials, "testuser")
        self.assertEqual(str(member), "testuser")

    def test_member_trello_uuid(self):
        member = Member.objects.create(user=self.user)
        TrelloMemberProfile.objects.create(member=member, trello_id="uuid123", username="test_trello_user", initials="TU")
        self.assertEqual(member.trello_member_profile.trello_id, "uuid123")
