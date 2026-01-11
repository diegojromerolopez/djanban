from django.urls import re_path
from djanban.apps.notifications import views




app_name = 'notifications'

urlpatterns = [
    re_path(r'^mark_as_read', views.mark_as_read, name="mark_as_read"),

]