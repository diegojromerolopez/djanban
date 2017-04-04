from django.conf.urls import url, include

from djangotrellostats.apps.forecaster.views.admin import index, test_forecaster, build_forecaster
from djangotrellostats.apps.forecaster.views.api import estimate

urlpatterns = [

    # Linear regression
    url(r'^$', index, name="index"),
    url(r'^test$', test_forecaster, name="test"),
    url(r'^build$', build_forecaster, name="build"),


    url(r'^api/estimate/(?P<card_id>\d+)$', estimate, name="estimate"),
]