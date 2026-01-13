from django.contrib import admin

from djanban.apps.dev_environment.models import Interruption, NoiseMeasurement

admin.site.register(NoiseMeasurement)
admin.site.register(Interruption)
