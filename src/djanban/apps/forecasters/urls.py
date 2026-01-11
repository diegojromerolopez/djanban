from django.urls import path, re_path

from djanban.apps.forecasters.views.admin import index, test_forecaster, build_forecaster, \
    ForecasterDelete, update_forecaster, view_forecaster


app_name = 'forecasters'

urlpatterns = [

    # Index
    path('', index, name="index"),

    # Regression test
    #url(r'^test$', test_forecaster, name="test"),

    # Regression model construction
    path('build', build_forecaster, name="build"),

    # Update a forecaster
    path('<int:forecaster_id>/update', update_forecaster, name="update"),
    # Test a forecaster
    re_path(r'^(?P<forecaster_id>\d+)/test', test_forecaster, name="test"),
    # View a forecaster
    re_path(r'^(?P<forecaster_id>\d+)/view', view_forecaster, name="view"),
    # Delete a forecaster
    path('<int:forecaster_id>/delete', ForecasterDelete.as_view(), name="delete"),

]