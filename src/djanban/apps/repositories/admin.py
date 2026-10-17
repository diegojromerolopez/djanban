from django.contrib import admin

from djanban.apps.repositories.models import GitHubPublicRepository, GitLabRepository

admin.site.register(GitLabRepository)
admin.site.register(GitHubPublicRepository)
