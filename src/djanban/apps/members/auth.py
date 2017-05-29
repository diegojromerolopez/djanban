# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from djanban.apps.base.auth import user_is_administrator, user_is_member


# Assert if current member can edit this member
def assert_user_can_edit_member(user, member):
    if user_is_administrator(user):
        return True

    if user_is_member(user):
        current_member = user.member
        # An user can edit another one if he/she is his/her creator or if is him/herself
        return current_member.id == member.creator_id or current_member.id == member.id

    raise AssertionError("You do not have permissions to edit this users")
