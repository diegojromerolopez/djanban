# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from djanban.apps.recurrent_cards.views import view_list, new, view, edit, delete

urlpatterns = [
    # List of work hours packages
    url(r'^$', view_list, name="view_list"),
    url(r'^new$', new, name="new"),
    url(r'^(?P<recurrent_card_id>\w+)/view/?$', view, name="view"),
    url(r'^(?P<recurrent_card_id>\w+)/edit/?$', edit, name="edit"),
    url(r'^(?P<recurrent_card_id>\w+)/delete/?$', delete, name="delete"),
]