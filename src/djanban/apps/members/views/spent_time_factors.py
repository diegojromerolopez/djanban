# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from djanban.apps.members.forms import SpentTimeFactorForm, DeleteSpentTimeForm
from djanban.apps.members.models import Member, SpentTimeFactor
from djanban.apps.members.views.main import assert_user_can_edit_member


# View list of spent factor for this member
@login_required
def view_list(request, member_id):
    member = Member.objects.get(id=member_id)

    # Check if current user has permissions to change his/her spent factors
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    spent_time_factors = member.spent_time_factors.all().order_by("start_date")

    replacements = {"member": member, "spent_time_factors": spent_time_factors}
    return render(request, "members/spent_time_factors/list.html", replacements)


# Add a new Spent Time Factor
@login_required
def add(request, member_id):
    member = Member.objects.get(id=member_id)

    # Check if current user has permissions to add new spent factor to this user
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    spent_time_factor = SpentTimeFactor(member=member)

    if request.method == "POST":

        form = SpentTimeFactorForm(request.POST, instance=spent_time_factor)
        if form.is_valid():
            form.save()
            _update_spent_time_factors(member)
            return HttpResponseRedirect(reverse("members:view_spent_time_factors", args=(member.id,)))

    else:
        form = SpentTimeFactorForm(instance=spent_time_factor)

    replacements = {"member": member, "form": form}
    return render(request, "members/spent_time_factors/add.html", replacements)


# Edit a Spent Time Factor
@login_required
def edit(request, member_id, spent_time_factor_id):
    member = Member.objects.get(id=member_id)

    # Check if current user has permissions to edit a spent factor to this user
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    spent_time_factor = get_object_or_404(SpentTimeFactor, id=spent_time_factor_id, member=member)

    if request.method == "POST":

        form = SpentTimeFactorForm(request.POST, instance=spent_time_factor)
        if form.is_valid():
            form.save()
            _update_spent_time_factors(member)
            return HttpResponseRedirect(reverse("members:view_spent_time_factors", args=(member.id,)))

    else:
        form = SpentTimeFactorForm(instance=spent_time_factor)

    replacements = {"member": member, "form": form}
    return render(request, "members/spent_time_factors/edit.html", replacements)


# Delete a Spent Time Factor
@login_required
def delete(request, member_id, spent_time_factor_id):
    member = Member.objects.get(id=member_id)

    # Check if current user has permissions to delete a spent factor to this user
    try:
        assert_user_can_edit_member(request.user, member)
    except AssertionError:
        return HttpResponseForbidden()

    spent_time_factor = get_object_or_404(SpentTimeFactor, id=spent_time_factor_id, member=member)

    if request.method == "POST":

        form = DeleteSpentTimeForm(request.POST)
        if form.is_valid():
            spent_time_factor.delete()
            _update_spent_time_factors(member)
            return HttpResponseRedirect(reverse("members:view_spent_time_factors", args=(member.id,)))

    else:
        form = DeleteSpentTimeForm()

    replacements = {"member": member, "form": form}
    return render(request, "members/spent_time_factors/delete.html", replacements)


# Update spent time factors for this member
def _update_spent_time_factors(member):
    for daily_spent_time in member.daily_spent_times.all():
        daily_spent_time.update_adjusted_spent_time()
