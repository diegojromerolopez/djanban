from django.urls import re_path

from djanban.apps.base.views import auth



app_name = 'base'

urlpatterns = [
    re_path(r'^login/?$', auth.login, name="login"),
    re_path(r'^logout/?$', auth.logout, name="logout"),
]
