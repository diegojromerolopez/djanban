# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import render

from djangotrellostats.apps.members.forms import GiveAccessToMemberForm
from djangotrellostats.apps.members.models import Member

# User dashboard
@login_required
def dashboard(request):
    member = request.user.member
    boards = member.boards.all()
    replacements = {"member": member, "boards": boards}
    return render(request, "members/dashboard.html", replacements)


# List of members
@login_required
def view_members(request):
    members = Member.objects.all()
    replacements = {"members": members}
    return render(request, "members/list.html", replacements)


# Give a password an create an user for a member if this member does not have an user yet
@login_required
def give_access_to_member(request, member_id):
    member = Member.objects.get(id=member_id)
    if request.method == "POST":

        form = GiveAccessToMemberForm(request.POST)
        if form.is_valid():
            member_email = form.cleaned_data["email"]
            member_password = form.cleaned_data["password"]
            print member_email
            print member_password

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

