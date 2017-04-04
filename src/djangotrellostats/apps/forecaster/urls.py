from django.conf.urls import url, include

from djangotrellostats.apps.forecaster.views.admin import index, test_forecaster, build_forecaster,\
    ForecasterDelete, update_forecaster, view_forecaster
from djangotrellostats.apps.forecaster.views.api import estimate

urlpatterns = [

    # Index
    url(r'^$', index, name="index"),

    # Regression test
    #url(r'^test$', test_forecaster, name="test"),

    # Regression model construction
    url(r'^build$', build_forecaster, name="build"),

    # Update a forecaster
    url(r'^(?P<forecaster_id>\d+)/update$', update_forecaster, name="update"),
    # Test a forecaster
    url(r'^(?P<forecaster_id>\d+)/test', test_forecaster, name="test"),
    # View a forecaster
    url(r'^(?P<forecaster_id>\d+)/view', view_forecaster, name="view"),
    # Delete a forecaster
    url(r'^(?P<forecaster_id>\d+)/delete$', ForecasterDelete.as_view(), name="delete"),

    # API that returns all estimations
    url(r'^api/estimate/(?P<card_id>\d+)$', estimate, name="estimate"),

]
