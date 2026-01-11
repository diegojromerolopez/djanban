from django.urls import path, re_path

from djanban.apps.niko_niko_calendar.views import view_calendar, new_mood_measurement



app_name = 'niko_niko_calendar'

urlpatterns = [
    # View the niko-niko calendar
    path('', view_calendar, name="view_calendar"),
    # Create a new mood measurement
    re_path(r'^new_mood_measurement', new_mood_measurement, name="new_mood_measurement"),
]
