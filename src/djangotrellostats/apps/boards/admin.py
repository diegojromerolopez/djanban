from django.contrib import admin

# Register your models here.
from djangotrellostats.apps.boards.models import List, ListReport, MemberReport, Card, Board, Label

admin.site.register(Board)
admin.site.register(Card)
admin.site.register(MemberReport)
admin.site.register(ListReport)
admin.site.register(List)
admin.site.register(Label)