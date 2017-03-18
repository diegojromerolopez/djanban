# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms import models
from django.utils import timezone
from trello import TrelloClient
from trello.member import Member as TrelloMember

from djangotrellostats.apps.members.models import Member, TrelloMemberProfile, SpentTimeFactor


# Register form
class LocalSignUpForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(LocalSignUpForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(label=u"First name", max_length=64, required=True)
        self.fields["last_name"] = forms.CharField(label=u"Last name", max_length=64, required=True)
        self.fields["email"] = forms.EmailField(label=u"Email and username", max_length=64, required=True)

        self.fields["password1"] = forms.CharField(label=u"Password", widget=forms.PasswordInput(), max_length=16, required=True)
        self.fields["password2"] = forms.CharField(label=u"Repeat your password", widget=forms.PasswordInput(), max_length=16, required=True)

        self.fields["captcha"] = CaptchaField(label=u"Fill this captcha to sign up")

    def clean(self):
        cleaned_data = super(LocalSignUpForm, self).clean()
        # Check if passwords are equal
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError(u"Passwords don't match")

        if cleaned_data.get("email"):
            # Check if username is unique
            cleaned_data["username"] = cleaned_data["email"]
            if User.objects.filter(username=cleaned_data["username"]).exists():
                raise ValidationError(u"You have already an user. Have you forgotten your password?")

        return self.cleaned_data

    def save(self, commit=False):
        member = Member()

        user = User(
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name"),
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
        )

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            member.user = user
            member.max_number_of_boards = Member.DEFAULT_MAX_NUMBER_OF_BOARDS
            member.save()

        return member


# Register form
class TrelloSignUpForm(LocalSignUpForm):

    def __init__(self, *args, **kwargs):
        super(TrelloSignUpForm, self).__init__(*args, **kwargs)

        self.fields["api_key"] = forms.CharField(label=u"Trello's API key", max_length=64, required=True)
        self.fields["token"] = forms.CharField(label=u"Trello's token", max_length=64, required=True)
        self.fields["token_secret"] = forms.CharField(label=u"Trello's token secret", max_length=64, required=True)

        self.order_fields(["first_name", "last_name", "email", "password1", "password2",
                           "api_key", "token", "token_secret", "captcha"])

    def clean(self):
        cleaned_data = super(TrelloSignUpForm, self).clean()

        # Get Trello remote data
        trello_client = TrelloClient(
            api_key=self.cleaned_data["api_key"], api_secret="xxx",
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
        member = super(TrelloSignUpForm, self).save(commit=True)

        trello_member_profile = TrelloMemberProfile(
            api_key=self.cleaned_data["api_key"],
            api_secret="xxx",
            token=self.cleaned_data["token"],
            token_secret=self.cleaned_data["token_secret"],
            trello_id=self.cleaned_data["uuid"],
            username=self.cleaned_data["trello_username"],
            initials=self.cleaned_data["initials"],
        )

        if commit:
            trello_member_profile.member = member
            trello_member_profile.save()

        return member


# Edition of the Member
class MemberForm(models.ModelForm):

    class Meta:
        model = Member
        fields = ["biography", "is_public"]

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields["first_name"] = forms.CharField(label=u"First name", max_length=64, required=True)
        self.fields["last_name"] = forms.CharField(label=u"Last name", max_length=64, required=True)
        self.fields["email"] = forms.EmailField(label=u"Email and username", max_length=64, required=True)
        self.fields["password1"] = forms.CharField(label=u"Password", widget=forms.PasswordInput(), max_length=16,
                                                   required=True)
        self.fields["password2"] = forms.CharField(label=u"Repeat the password", widget=forms.PasswordInput(),
                                                   max_length=16, required=True)
        self.order_fields(["first_name", "last_name", "email", "password", "password", "biography"])

        # Default values
        if self.instance.user:
            self.initial["first_name"] = self.instance.user.first_name
            self.initial["last_name"] = self.instance.user.last_name
            self.initial["email"] = self.instance.user.email

    def clean(self):
        cleaned_data = super(MemberForm, self).clean()
        # Check if passwords are equal
        if cleaned_data.get("password1") and cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError(u"Passwords don't match")

        if cleaned_data.get("password1"):
            cleaned_data["password"] = cleaned_data.get("password1")

        if cleaned_data.get("email"):
            # Check if username is unique
            cleaned_data["username"] = cleaned_data["email"]
            if User.objects.filter(username=cleaned_data["username"]).exists():
                raise ValidationError(u"You have already an user. Have you forgotten your password?")

        return self.cleaned_data

    def save(self, commit=True):
        if not self.instance.user:
            user = User()
        else:
            user = self.instance.user

        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.username = self.cleaned_data.get("username")
        user.email = self.cleaned_data.get("email")

        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
            self.instance.user = user
            self.instance.save()

        return self.instance


# Administrator edits a member profile
class AdminMemberForm(MemberForm):
    class Meta(MemberForm.Meta):
        model = Member
        fields = ["biography", "is_developer", "on_holidays", "minimum_working_hours_per_day",
                  "minimum_working_hours_per_week", "is_public"]

    def __init__(self, *args, **kwargs):
        super(AdminMemberForm, self).__init__(*args, **kwargs)

        self.order_fields(["first_name", "last_name", "email", "password", "password", "biography",
                           "is_developer", "on_holidays", "minimum_working_hours_per_day",
                           "minimum_working_hours_per_week", "spent_time_factor"])


# Edition of the Trello Member profile
class TrelloMemberProfileForm(models.ModelForm):

    class Meta:
        model = TrelloMemberProfile
        fields = ["api_key", "api_secret", "token", "token_secret"]

    def __init__(self, *args, **kwargs):
        super(TrelloMemberProfileForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(TrelloMemberProfileForm, self).clean()

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
        self.cleaned_data["username"] = trello_member.username
        self.cleaned_data["initials"] = trello_member.initials

        return self.cleaned_data

    def save(self, commit=True):
        super(TrelloMemberProfileForm, self).save(commit=False)

        if commit:
            self.instance.trello_id = self.cleaned_data["uuid"]
            self.instance.username = self.cleaned_data["username"]
            self.instance.initials = self.cleaned_data["initials"]
            self.instance.member = self.instance.member
            self.instance.save()

        return self.instance


# Give access to member form
class GiveAccessToMemberForm(forms.Form):
    email = forms.EmailField(label=u"Email and username")
    password = forms.CharField(label=u"Password", widget=forms.PasswordInput)


# Change password to member user
class ChangePasswordToMemberForm(forms.Form):
    password1 = forms.CharField(label=u"Password", widget=forms.PasswordInput(), max_length=16, required=True)
    password2 = forms.CharField(label=u"Repeat your password", widget=forms.PasswordInput(), max_length=16,
                                required=True)

    def clean(self):
        cleaned_data = super(ChangePasswordToMemberForm, self).clean()
        # Check if passwords are equal
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError(u"Passwords don't match")


# Edit your member profile
class EditTrelloMemberProfileForm(ModelForm):

    class Meta:
        model = TrelloMemberProfile
        fields = ["api_key", "api_secret", "token", "token_secret"]

    def __init__(self, *args, **kwargs):
        super(EditTrelloMemberProfileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        super(EditTrelloMemberProfileForm, self).save(commit=commit)


# Assigns a new password to one user that has forgotten it
class ResetPasswordForm(forms.Form):
    trello_username = forms.CharField(label=u"Trello username")
    email = forms.EmailField(label=u"Email and username")

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        try:
            members = Member.objects.filter(user__email=cleaned_data.get("email"), user__is_active=True)
            cleaned_data["members"] = members
        except Member.DoesNotExist:
            raise ValidationError(u"Member does not exist, the username or email is wrong")

        return cleaned_data


# Spent time factor form
class SpentTimeFactorForm(ModelForm):
    class Meta:
        model = SpentTimeFactor
        fields = ("name", "start_date", "end_date", "factor")
        widgets = {
            'start_date': forms.SelectDateWidget(),
            'end_date': forms.SelectDateWidget(empty_label=u"Until now"),
        }

    def __init__(self, *args, **kwargs):
        super(SpentTimeFactorForm, self).__init__(*args, **kwargs)
        current_year = timezone.now().year
        available_years = [year_i for year_i in range(current_year-40, current_year+1)]
        self.fields["start_date"].widget.years = available_years
        self.fields["end_date"].widget.years = available_years


# Delete a spent time form
class DeleteSpentTimeForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm the deletion of this spent time factor")
