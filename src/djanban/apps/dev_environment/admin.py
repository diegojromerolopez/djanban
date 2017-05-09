# -*- coding: utf-8 -*-

from django.contrib import admin

from djanban.apps.dev_environment.models import NoiseMeasurement, Interruption

admin.site.register(NoiseMeasurement)
admin.site.register(Interruption)
