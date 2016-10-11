# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from trello import TrelloClient


# Establishes a connection with Trello API
class TrelloConnector(object):
    def __init__(self, member):
        self.member = member
        self.trello_client = self._get_trello_client()

    # Get a trello client for this user
    def _get_trello_client(self):
        client = TrelloClient(
            api_key=self.member.api_key,
            api_secret=self.member.api_secret,
            token=self.member.token,
            token_secret=self.member.token_secret
        )
        return client
