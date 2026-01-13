from django.urls import path

from djanban.apps.slideshow.views import view

app_name = "slideshow"

urlpatterns = [
    path("", view, name="view"),
]
