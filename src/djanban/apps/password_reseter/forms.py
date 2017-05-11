
from __future__ import unicode_literals

from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import PasswordInput

from djanban.apps.password_reseter.models import PasswordResetRequest


# Request new password form
class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(label=u"Username")
    captcha = CaptchaField(label=u"Fill this captcha to reset your password")

    def clean(self):
        cleaned_data = super(RequestPasswordResetForm, self).clean()
        user = User.objects.get(username=self.cleaned_data["username"])

        # Check if user ir valid
        if not user or not user.is_active:
            raise ValidationError(u"Your username is invalid. Is that right?")

        # Check if there is any other pending password reset request
        if PasswordResetRequest.user_has_a_pending_new_password_request(user):
            raise ValidationError(u"You already has a pending password request.")

        cleaned_data["user"] = user
        return cleaned_data


# Reset password form
class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label=u"Password", widget=PasswordInput())
    password2 = forms.CharField(label=u"Introduce again your password", widget=PasswordInput())
    captcha = CaptchaField(label=u"Fill this captcha to reset your password")

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise ValidationError("Passwords don't match")
        return cleaned_data
