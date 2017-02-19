# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render

from djangotrellostats.apps.base.auth import user_is_administrator, get_user_boards, user_is_member
from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.members.decorators import administrator_required
from djangotrellostats.apps.members.forms import GiveAccessToMemberForm, ChangePasswordToMemberForm, EditTrelloMemberProfileForm, AdminMemberForm, \
    MemberForm
from djangotrellostats.apps.members.models import Member


# User dashboard
@member_required
def dashboard(request):
    member = request.user.member
    boards = member.boards.all()
    replacements = {"member": member, "boards": boards}
    return render(request, "members/dashboard.html", replacements)


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

        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = MemberForm(instance=member)

    replacements = {"member": member, "form": form}
    return render(request, "members/new.html", replacements)


# Give a password an create an user for a member if this member does not have an user yet
@member_required
@administrator_required
def give_access_to_member(request, member_id):
    member = Member.objects.get(id=member_id)
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
@member_required
def change_password_to_member(request, member_id):
    member = Member.objects.get(id=member_id)
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


@member_required
def edit_profile(request, member_id):
    user = request.user
    current_member = user.member

    member = Member.objects.get(id=member_id)

    # Check if the current member is editing his/her profile or the current member is his/her creator or
    # is an administrator
    if current_member.id != int(member_id) and current_member.id != member.creator_id and not user_is_administrator(user):
        return HttpResponseForbidden()

    # Only the administrator has permission of a full change of member attributes
    Form = MemberForm
    if user_is_administrator(user):
        Form = AdminMemberForm

    if request.method == "POST":

        form = Form(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("members:view_members"))

    else:
        form = Form(instance=member)

    replacements = {"member": member, "form": form}
    return render(request, "members/edit_profile.html", replacements)


# Change your user profile data
@member_required
def edit_trello_member_profile(request, member_id):
    user = request.user
    current_member = user.member

    member = Member.objects.get(id=member_id)
    if current_member.id != int(member_id) and current_member.id != member.creator_id and not user_is_administrator(user):
        return HttpResponseForbidden()

    # Only the administrator has permission of a full change of member attributes
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