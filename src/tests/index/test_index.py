# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class IndexTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )

    def test_index_view_anonymous(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
