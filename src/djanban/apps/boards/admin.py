from django.contrib import admin

from djanban.apps.boards.models import Board, Card, Label, List

admin.site.register(Board)
admin.site.register(Card)
admin.site.register(List)
admin.site.register(Label)
