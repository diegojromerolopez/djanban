# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

from djanban.apps.base.auth import get_user_boards
from djanban.apps.boards.models import Board


# Login form
class LoginForm(forms.Form):
    username = forms.CharField(label=u"Visitor username")
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user = authenticate(username=cleaned_data.get("username"), password=cleaned_data.get("password"))

        if not user or not user.is_active:
            raise ValidationError(u"Your authentication data is invalid. Please check your username and password")

        cleaned_data["user"] = user
        return cleaned_data


# New user form
class NewUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = forms.CharField(label=u"Password", widget=forms.PasswordInput(),
                                                   required=True)
        self.fields["password2"] = forms.CharField(label=u"Repeat password", widget=forms.PasswordInput(),
                                                   required=True)

        current_request = CrequestMiddleware.get_request()
        boards = get_user_boards(current_request.user).filter(is_archived=False).order_by("name")
        self.fields["boards"] = forms.MultipleChoiceField(
            label=u"Boards",
            choices=[(board.id, board.name) for board in boards],
            help_text=u"Boards this visitor will have access",
            required=False
        )
        self.fields["boards"].widget.attrs = {'size': boards.count()}

    # Clean form
    def clean(self):
        cleaned_data = super(NewUserForm, self).clean()

        # Check if he/she has at least one board
        if len(self.cleaned_data["boards"]) == 0:
            raise ValidationError(u"Please select at least one board for this visitor")

        # Check if passwords match
        if self.cleaned_data.get("password1") \
                and self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise ValidationError(u"Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        super(NewUserForm, self).save(commit=False)
        if commit:
            # Change password if both passwords match
            if self.cleaned_data.get("password1") \
                    and self.cleaned_data.get("password1") == self.cleaned_data.get("password2"):

                self.instance.set_password(self.cleaned_data.get("password1"))
                self.instance.save()

            # Add user to visitors groups
            visitors = Group.objects.get(name='Visitors')
            if self.instance.id is None or not visitors.user_set.filter(id=self.instance.id).exists():
                visitors.user_set.add(self.instance)

            # Add boards to visitor
            boards = self.cleaned_data["boards"]
            self.instance.boards.clear()
            for board in boards:
                if not self.instance.boards.filter(id=board).exists():
                    self.instance.boards.add(board)

            self.instance.save()

        return self.instance


# Edit visitor
class EditUserForm(NewUserForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "is_active"]

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password1"].help_text = u"Keep this field blank if you don't want to change the password"
        self.fields["password2"].required = False
        self.fields["password2"].help_text = u"Keep this field blank if you don't want to change the password"
        current_request = CrequestMiddleware.get_request()
        boards = get_user_boards(current_request.user).filter(is_archived=False).order_by("name")
        self.fields["boards"] = forms.MultipleChoiceField(
            label=u"Boards",
            choices=[(board.id, board.name) for board in boards],
            initial=[board.id for board in self.instance.boards.all().order_by("name")],
            help_text=u"Boards this visitor will have access",
            required=False,
        )
        self.fields["boards"].widget.attrs={'size': boards.count()}

    def save(self, commit=True):
        super(EditUserForm, self).save(commit=True)


# Delete a visitor
class DeleteUserForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this user")