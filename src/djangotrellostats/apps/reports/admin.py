from django.contrib import admin

from djangotrellostats.apps.reports.models import MemberReport, ListReport

admin.site.register(MemberReport)
admin.site.register(ListReport)