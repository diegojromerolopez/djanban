from django.urls import re_path as url

from djanban.apps.forecasters.views.admin import (
    ForecasterDelete,
    build_forecaster,
    index,
    test_forecaster,
    update_forecaster,
    view_forecaster,
)

app_name = "forecasters"

urlpatterns = [
    # Index
    url(r"^$", index, name="index"),
    # Regression test
    # url(r'^test$', test_forecaster, name="test"),
    # Regression model construction
    url(r"^build$", build_forecaster, name="build"),
    # Update a forecaster
    url(r"^(?P<forecaster_id>\d+)/update$", update_forecaster, name="update"),
    # Test a forecaster
    url(r"^(?P<forecaster_id>\d+)/test", test_forecaster, name="test"),
    # View a forecaster
    url(r"^(?P<forecaster_id>\d+)/view", view_forecaster, name="view"),
    # Delete a forecaster
    url(r"^(?P<forecaster_id>\d+)/delete$", ForecasterDelete.as_view(), name="delete"),
]
