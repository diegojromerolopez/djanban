# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from djanban.apps.base.auth import user_is_member, user_is_administrator
from djanban.apps.base.decorators import member_required
from djanban.apps.work_hours_packages.forms import WorkHoursPackageForm, DeleteWorkHoursPackageForm, \
    NotificationCompletionSenderForm, WorkHoursPackageFilterForm
from djanban.apps.work_hours_packages.models import WorkHoursPackage
from djanban.apps.base.views import models as model_views


# New work hours package
@member_required
def new(request):
    member = request.user.member
    work_hours_package = WorkHoursPackage(creator=request.user.member)
    return model_views.new(
        request, instance=work_hours_package,
        form_class=WorkHoursPackageForm, extra_form_parameters={"member": member},
        template_path="work_hours_packages/new.html", ok_url=reverse("work_hours_packages:view_list")
    )


# Edition of a work hours package
@member_required
def edit(request, work_hours_package_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
        try:
            work_hours_package = member.created_work_hours_packages.get(id=work_hours_package_id)
        except WorkHoursPackage.DoesNotExist:
            raise Http404
    elif user_is_administrator(request.user):
        work_hours_package = WorkHoursPackage.objects.get(id=work_hours_package_id)

    return model_views.edit(
        request, instance=work_hours_package,
        form_class=WorkHoursPackageForm, extra_form_parameters={"member": member},
        template_path="work_hours_packages/edit.html",
        ok_url=reverse("work_hours_packages:view_list")
    )


@login_required
def notify_completions(request):
    member = None
    if user_is_member(request.user):
        member = request.user.member
    if request.method == "POST":
        form = NotificationCompletionSenderForm(request.POST, member=member)

        if form.is_valid():
            form.send()
            return HttpResponseRedirect(reverse("work_hours_packages:view_list"))
    else:
        form = NotificationCompletionSenderForm(member=member)

    replacements = {"form": form, "member": member}
    return render(request, "work_hours_packages/notify_completions.html", replacements)


# View a work hours package
@login_required
def view(request, work_hours_package_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
        try:
            work_hours_package = member.work_hours_packages.get(id=work_hours_package_id)
        except WorkHoursPackage.DoesNotExist:
            raise Http404
    elif user_is_administrator(request.user):
        work_hours_package = WorkHoursPackage.objects.get(id=work_hours_package_id)

    replacements = {"work_hours_package": work_hours_package, "member": member}
    return render(request, "work_hours_packages/view.html", replacements)


# View all work hours packages
@login_required
def view_list(request):
    member = None
    form = None
    if user_is_member(request.user):
        member = request.user.member
        form = WorkHoursPackageFilterForm(request.GET, member=member)

    if form and form.is_valid():
        work_hours_packages = form.get_work_hours_packages()
    else:
        if member:
            work_hours_packages = member.work_hours_packages.all().order_by("start_work_date", "end_work_date", "name")
        elif user_is_administrator(request.user):
            work_hours_packages = WorkHoursPackage.objects.order_by("start_work_date", "end_work_date", "name")

    replacements = {"work_hours_packages": work_hours_packages, "member": member, "form": form}
    return render(request, "work_hours_packages/list.html", replacements)


# Delete a work hours package
@login_required
def delete(request, work_hours_package_id):
    member = None
    if user_is_member(request.user):
        member = request.user.member
        try:
            work_hours_package = member.created_work_hours_packages.get(id=work_hours_package_id)
        except WorkHoursPackage.DoesNotExist:
            raise Http404
    elif user_is_administrator(request.user):
        work_hours_package = WorkHoursPackage.objects.get(id=work_hours_package_id)
    return model_views.delete(
        request, instance=work_hours_package, form_class=DeleteWorkHoursPackageForm,
        next_url=reverse("work_hours_packages:view_list"),
        template_path="work_hours_packages/delete.html", template_replacements={"member":member}
    )
