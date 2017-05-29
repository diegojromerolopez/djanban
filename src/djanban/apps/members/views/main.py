# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import render

from djanban.apps.base.auth import user_is_administrator, get_user_boards, user_is_member
from djanban.apps.base.decorators import member_required
from djanban.apps.members.auth import assert_user_can_edit_member
from djanban.apps.members.decorators import administrator_required
from djanban.apps.members.forms import GiveAccessToMemberForm, ChangePasswordToMemberForm,\
    EditTrelloMemberProfileForm, EditMemberForm, NewMemberForm, EditAdminMemberForm
from djanban.apps.members.models import Member


# User dashboard
from djanban.apps.members.views.emailer import send_new_member_email


# List of members
@login_required
def view_members(request):
    current_user = request.user
    boards = get_user_boards(current_user)
    if user_is_member(current_user):
        member = request.user.member
        members = Member.objects.filter(Q(boards__in=boards) | Q(creator=current_user.member) | Q(is_public=True)).distinct()
    else:
        member = None
        members = Member.objects.filter(boards__in=boards).distinct()

    replacements = {
        "member": member,
        "members": members,
        "developers": Member.objects.filter(is_developer=True)
    }
    return render(request, "members/list.html", replacements)


# Create a new member
@member_required
def new(request):
    user = request.user
    current_member = user.member

    member = Member(creator=current_member, is_public=False)
    if request.method == "POST":

        form = NewMemberForm(request.POST, instance=member)
        if form.is_valid():
            with transaction.atomic():
                form.save(commit=True)
                member_password = form.cleaned_data.get("password")
                send_new_member_email(member, member_password)
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = NewMemberForm(instance=member)

    replacements = {"member": member, "form": form}
    return render(request, "members/new.html", replacements)


# Give a password an create an user for a member if this member does not have an user yet
@login_required
def give_access_to_member(request, member_id):
    member = Member.objects.get(id=member_id)

    # Check if the current user is an administrator or the creator of this member or the member him/herself
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    if request.method == "POST":

        form = GiveAccessToMemberForm(request.POST)
        if form.is_valid():
            member_email = form.cleaned_data["email"]
            member_password = form.cleaned_data["password"]

            if member.user is None:
                user = User(username=member_email, email=member_email)
                user.set_password(member_password)
                user.save()
                member.user = user

            else:
                user = member.user
                user.set_password(member_password)
                user.save()

            member.save()
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = GiveAccessToMemberForm()

    replacements = {"member": member, "form": form}
    return render(request, "members/give_access_to_member.html", replacements)


# Change password to an user of a member
@login_required
def change_password_to_member(request, member_id):
    member = Member.objects.get(id=member_id)

    # Check if the current user is an administrator or the creator of this member or the member him/herself
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    if request.method == "POST":

        form = ChangePasswordToMemberForm(request.POST)
        if form.is_valid():
            member_password = form.cleaned_data["password1"]
            user = member.user
            user.set_password(member_password)
            user.save()
            if request.user.id == member.user_id:
                return HttpResponseRedirect(reverse("index"))
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = ChangePasswordToMemberForm()

    replacements = {"member": member, "form": form}
    return render(request, "members/give_access_to_member.html", replacements)


# Edit member profile
@login_required
def edit_profile(request, member_id):
    user = request.user

    member = Member.objects.get(id=member_id)

    if hasattr(user, "member"):
        current_member = user.member
        current_user_is_admin_for_this_member = current_member.id != member.creator_id
    else:
        current_user_is_admin_for_this_member = user_is_administrator(user)

    # Check if the current user is an administrator or the creator of this member or the member him/herself
    try:
        assert_user_can_edit_member(user, member)
    except AssertionError:
        return HttpResponseForbidden()

    # Only the administrator has permission of a full change of member attributes
    Form = EditMemberForm
    if current_user_is_admin_for_this_member:
        Form = EditAdminMemberForm

    if request.method == "POST":

        form = Form(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = Form(instance=member)

    replacements = {"member": member, "form": form}
    return render(request, "members/edit_profile.html", replacements)


# Change your user profile data
@login_required
def edit_trello_member_profile(request, member_id):
    user = request.user

    member = Member.objects.get(id=member_id)

    # Check if the current user is an administrator or the creator of this member or the member him/herself
    try:
        assert_user_can_edit_member(user, member)
    except AssertionError:
        return HttpResponseForbidden()

    # Edition of Trello Profile
    Form = EditTrelloMemberProfileForm

    if request.method == "POST":

        form = Form(request.POST, instance=member.trello_member_profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = Form(instance=member.trello_member_profile)

    replacements = {"member": member, "form": form}
    return render(request, "members/edit_trello_profile.html", replacements)




