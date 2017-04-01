from django.conf.urls import url, include

from djangotrellostats.apps.forecaster.views import test_forecaster

urlpatterns = [

    # Linear regression
    url(r'^test', test_forecaster, name="test"),
]