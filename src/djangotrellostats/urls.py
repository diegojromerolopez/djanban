"""djangoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from djangotrellostats.apps.public import views as public_views

urlpatterns = [
    url(r'^$', public_views.index, name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^member/', include('djangotrellostats.apps.members.urls', namespace="members")),
    url(r'^boards/', include('djangotrellostats.apps.boards.urls', namespace="boards")),
    #url(r'^connector/', include('djangotrellostats.apps.connector.urls', namespace="connector")),
    #url(r'^taskboard/', include('djangotrellostats.apps.taskboard.urls', namespace="taskboard")),
]
