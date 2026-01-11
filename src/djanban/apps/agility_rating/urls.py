from django.urls import path

from djanban.apps.agility_rating.views import view, new, edit, delete



app_name = 'agility_rating'

urlpatterns = [
    path('', view, name="view"),
    path('new', new, name="new"),
    path('edit', edit, name="edit"),
    path('delete', delete, name="delete"),
]