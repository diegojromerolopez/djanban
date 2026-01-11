from django.urls import path, re_path

from djanban.apps.repositories.views.repositories import view_list, new, view, edit, delete, checkout
from djanban.apps.repositories.views.commits import add as add_commit, delete as delete_commit, \
    view_assessment_report



app_name = 'repositories'

urlpatterns = [

    # List of repositories of this project
    path('', view_list, name="view_repositories"),

    re_path(r'^(?P<type>gitlab)/new/?$', new, name="new_repository"),
    re_path(r'^(?P<type>github)/new/?$', new, name="new_repository"),

    re_path(r'^(?P<repository_id>\d+)/view/?$', view, name="view_repository"),

    re_path(r'^(?P<repository_id>\d+)/checkout/?$', checkout, name="checkout_repository"),

    re_path(r'^(?P<repository_id>\d+)/commits/add/?$', add_commit, name="add_commit"),

    re_path(r'^(?P<repository_id>\d+)/commits/(?P<commit_id>\d+)/view_assessment_report/?$', view_assessment_report, name="view_assessment_report"),

    re_path(r'^(?P<repository_id>\d+)/commits/(?P<commit_id>\d+)/delete/?$', delete_commit, name="delete_commit"),

    re_path(r'^(?P<repository_id>\d+)/edit/?$', edit, name="edit_repository"),

    re_path(r'^(?P<repository_id>\d+)/delete/?$', delete, name="delete_repository"),
]