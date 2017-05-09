

# User login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from djanban.apps.visitors.forms import LoginForm
from django.contrib.auth import login as django_login


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            django_login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = LoginForm()

    return render(request, "members/login.html", {"form": form})


# User logout
@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse("index"))