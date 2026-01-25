# -*- coding: utf-8 -*-


from django.urls import re_path as url

from djanban.apps.recurrent_cards.views import delete, edit, new, view, view_list

app_name = "recurrent_cards"

urlpatterns = [
    # List of work hours packages
    url(r"^$", view_list, name="view_list"),
    url(r"^new$", new, name="new"),
    url(r"^(?P<recurrent_card_id>\w+)/view/?$", view, name="view"),
    url(r"^(?P<recurrent_card_id>\w+)/edit/?$", edit, name="edit"),
    url(r"^(?P<recurrent_card_id>\w+)/delete/?$", delete, name="delete"),
]
