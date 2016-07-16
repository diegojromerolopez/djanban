# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import models
from trello import TrelloClient

from djangotrellostats.apps.members.models import Member

from trello.member import Member as TrelloMember


# Register form
class SignUpForm(models.ModelForm):
    class Meta:
        model = Member
        fields = ["api_key", "api_secret", "token", "token_secret"]

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(label=u"First name", max_length=64, required=True)
        self.fields["last_name"] = forms.CharField(label=u"Last name", max_length=64, required=True)
        self.fields["email"] = forms.EmailField(label=u"Email and username", max_length=64, required=True)
        self.fields["password1"] = forms.CharField(label=u"Password", widget=forms.PasswordInput(), max_length=16, required=True)
        self.fields["password2"] = forms.CharField(label=u"Repeat your password", widget=forms.PasswordInput(), max_length=16, required=True)

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        # Check if passwords are equal
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError(u"Passwords don't match")

        if cleaned_data.get("email"):
            # Check if username is unique
            cleaned_data["username"] = cleaned_data["email"]
            if User.objects.filter(username=cleaned_data["username"]).exists():
                raise ValidationError(u"You have already an user. Have you forgotten your password?")

        # Get Trello remote data
        trello_client = TrelloClient(
            api_key=self.cleaned_data["api_key"], api_secret=self.cleaned_data["api_secret"],
            token=self.cleaned_data["token"], token_secret=self.cleaned_data["token_secret"]
        )

        trello_member = TrelloMember(client=trello_client, member_id="me")
        try:
            trello_member.fetch()
        except Exception:
            raise ValidationError(u"Exception when dealing with Trello connection. Are your credentials right?")

        self.cleaned_data["uuid"] = trello_member.id
        self.cleaned_data["trello_username"] = trello_member.username
        self.cleaned_data["initials"] = trello_member.initials

        return self.cleaned_data

    def save(self, commit=False):
        member = super(SignUpForm, self).save(commit=False)

        user = User(
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
        )

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            # If there is a member with the same username and has not been reclaimed, reclaim it
            if Member.objects.filter(trello_username=self.cleaned_data["username"], user=None).exists():
                member = Member.objects.get(trello_username=self.cleaned_data["username"])

            member.api_key = self.cleaned_data["api_key"]
            member.api_secret = self.cleaned_data["api_secret"]
            member.token = self.cleaned_data["token"]
            member.token_secret = self.cleaned_data["token_secret"]
            member.uuid = self.cleaned_data["uuid"]
            member.trello_username = self.cleaned_data["trello_username"]
            member.initials = self.cleaned_data["initials"]
            member.user = user
            member.save()

        return member


# Login form
class LoginForm(forms.Form):
    username = forms.EmailField(label=u"Email and username")
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user = authenticate(username=cleaned_data.get("username"), password=cleaned_data.get("password"))

        if not user or not user.is_active:
            raise ValidationError(u"Your authentication data is invalid. Please check your username and password")

        cleaned_data["user"] = user
        return cleaned_data


# Give access to member form
class GiveAccessToMemberForm(forms.Form):
    email = forms.EmailField(label=u"Email and username")
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)

