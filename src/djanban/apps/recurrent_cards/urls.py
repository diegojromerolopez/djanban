from django.urls import path, re_path

from djanban.apps.recurrent_cards.views import view_list, new, view, edit, delete



app_name = 'recurrent_cards'

urlpatterns = [
    # List of work hours packages
    path('', view_list, name="view_list"),
    path('new', new, name="new"),
    re_path(r'^(?P<recurrent_card_id>\w+)/view/?$', view, name="view"),
    re_path(r'^(?P<recurrent_card_id>\w+)/edit/?$', edit, name="edit"),
    re_path(r'^(?P<recurrent_card_id>\w+)/delete/?$', delete, name="delete"),
]