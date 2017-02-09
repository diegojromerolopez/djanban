# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from trello import TrelloClient


# Establishes a connection with Trello API
class TrelloConnector(object):
    def __init__(self, member):
        self.member = member
        self.trello_member_profile = member.trello_member_profile
        self.trello_client = self._get_trello_client()

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.trello_member_profile.api_key,
            api_secret=self.trello_member_profile.api_secret,
            token=self.trello_member_profile.token,
            token_secret=self.trello_member_profile.token_secret
        )
        return client
