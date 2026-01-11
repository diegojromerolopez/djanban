# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from djanban.remote_backends.native.connector import NativeConnector
from djanban.remote_backends.trello.connector import TrelloConnector


# Backend factory
class RemoteBackendConnectorFactory(object):

    @staticmethod
    def factory(member):
        # If the member is paired with a Trello Member, the remote backend is Trello
        if member.has_trello_profile:
            return TrelloConnector(member)
        # Otherwise, the remote backend is a fake one, called "native" but really is none
        # this backend only initializes some object attributes and of course makes no
        # local object save because that's the responsibility of the method that calls the operation
        else:
            return NativeConnector(member)