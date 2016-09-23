from django.contrib import admin

from djangotrellostats.apps.repositories.models import GitLabRepository, GitHubPublicRepository

admin.site.register(GitLabRepository)
admin.site.register(GitHubPublicRepository)
