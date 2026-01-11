from django.urls import re_path
from django.views.generic import TemplateView

from djanban.apps.members.views import auth, main, spent_time_factors



app_name = 'members'

urlpatterns = [
    re_path(r'^signup/?$', auth.signup, name="signup"),
    re_path(r'^signup/local/?$', auth.local_signup, name="local_signup"),
    re_path(r'^signup/trello/?$', auth.trello_signup, name="trello_signup"),

    re_path(r'^reset_password/?$', auth.reset_password, name="reset_password"),
    re_path(r'^reset_password_success/?$', TemplateView.as_view(template_name="members/reset_password_success.html"),
        name="reset_password_success"),

    re_path(r'^new/?$', main.new, name="new"),
    re_path(r'^view_members/?$', main.view_members, name="view_members"),

    re_path(r'^(?P<member_id>\d+)/give_access/?$', main.give_access_to_member, name="give_access"),
    re_path(r'^(?P<member_id>\d+)/change_password/?$', main.change_password_to_member, name="change_password"),

    # Member profile
    re_path(r'^(?P<member_id>\d+)/edit/?$', main.edit_profile, name="edit_profile"),
    re_path(r'^(?P<member_id>\d+)/edit/trello/?$', main.edit_trello_member_profile, name="edit_trello_member_profile"),

    # Spent time factors
    re_path(r'^(?P<member_id>\d+)/spent_time_factors/?$', spent_time_factors.view_list, name="view_spent_time_factors"),
    re_path(r'^(?P<member_id>\d+)/spent_time_factors/add/?$', spent_time_factors.add, name="new_spent_time_factor"),
    re_path(r'^(?P<member_id>\d+)/spent_time_factors/(?P<spent_time_factor_id>\d+)/?$', spent_time_factors.edit, name="edit_spent_time_factor"),
    re_path(r'^(?P<member_id>\d+)/spent_time_factors/(?P<spent_time_factor_id>\d+)/delete/?$', spent_time_factors.delete, name="delete_spent_time_factor"),

]