from django.contrib import admin

from djangotrellostats.apps.boards.models import List, Card, Board, Label

admin.site.register(Board)
admin.site.register(Card)
admin.site.register(List)
admin.site.register(Label)