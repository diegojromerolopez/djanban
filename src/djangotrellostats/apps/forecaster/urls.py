from django.conf.urls import url, include

from djangotrellostats.apps.forecaster.views.admin import index, test_forecaster, build_forecaster
from djangotrellostats.apps.forecaster.views.api import estimate

urlpatterns = [

    # Index
    url(r'^$', index, name="index"),

    # Regression test
    url(r'^test$', test_forecaster, name="test"),

    # Regression model construction
    url(r'^build$', build_forecaster, name="build"),

    # API that returns all estimations
    url(r'^api/estimate/(?P<card_id>\d+)$', estimate, name="estimate"),

]
