from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from djanban.apps.boards.models import Board

from djanban.apps.visitors.forms import DeleteUserForm, NewUserForm, EditUserForm


# List all visitors
@login_required
def view_list(request, board_id=None):
    member = request.user.member
    visitor_group = Group.objects.get(name="Visitors")

    if board_id is None:
        visitor_users = visitor_group.user_set.all().order_by("username")
    else:
        board = get_object_or_404(Board, id=board_id)
        visitor_users = board.visitors.all().order_by("username")

    replacements = {"visitors": visitor_users, "member": member}
    return render(request, "visitors/list.html", replacements)


# New user
@login_required
def new(request):
    member = request.user.member
    user = User()

    if request.method == "POST":
        form = NewUserForm(request.POST, instance=user)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("visitors:view_list"))
    else:
        form = NewUserForm(instance=user)

    return render(request, "visitors/new.html", {"form": form, "user": user, "member": member})


# Edition of a visitor
@login_required
def edit(request, visitor_id):
    member = request.user.member
    visitor_group = Group.objects.get(name="Visitors")
    try:
        user = visitor_group.user_set.get(id=visitor_id)
    except User.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("visitors:view_list"))

    else:
        form = EditUserForm(instance=user)

    return render(request, "visitors/edit.html", {"form": form, "user": user, "member": member})


# Delete a visitor
@login_required
def delete(request, visitor_id):
    member = request.user.member
    visitor_group = Group.objects.get(name="Visitors")
    try:
        user = visitor_group.user_set.get(id=visitor_id)
    except User.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = DeleteUserForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            user.delete()
            return HttpResponseRedirect(reverse("visitors:view_list"))

    else:
        form = DeleteUserForm()

    return render(request, "visitors/delete.html", {"form": form, "user": user, "member": member})
