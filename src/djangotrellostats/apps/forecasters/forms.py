from crequest.middleware import CrequestMiddleware
from django import forms
from django.core.exceptions import ValidationError

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.forecasters.models import Forecaster
from djangotrellostats.apps.forecasters.regression.regressors import REGRESSION_MODELS
from djangotrellostats.apps.forecasters.regression.runner import RegressorRunner
from djangotrellostats.apps.members.models import Member


class BuildForecasterForm(forms.ModelForm):
    class Meta:
        model = Forecaster
        fields = ("model", "board", "member", "name")

    def __init__(self, *args, **kwargs):
        super(BuildForecasterForm, self).__init__(*args, **kwargs)

        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        boards = get_user_boards(current_user)
        members = Member.get_user_team_mates(current_user)
        self.fields["model"] = forms.ChoiceField(label="Regression model")
        self.fields["model"].choices = REGRESSION_MODELS
        self.fields["board"].choices = [("", "All")]+[(board.id, board.name) for board in boards]
        self.fields["member"].choices = [("", "None")] + [(member.id, member.external_username) for member in members]

    def clean(self):
        cleaned_data = super(BuildForecasterForm, self).clean()
        if cleaned_data.get("board") and cleaned_data.get("member"):
            raise ValidationError("Please, select board or member but not both.")
        return cleaned_data

    def save(self, commit=True):
        runner = RegressorRunner(self.instance.name, self.instance.model, self.instance.board, self.instance.member)
        return runner.run()


class UpdateForecasterForm(forms.Form):
    confirm = forms.BooleanField(label="I want to update this forecaster", required=True)

    def save(self, forecaster):
        name = forecaster.name
        model = forecaster.model.lower()
        board = forecaster.board
        member = forecaster.member
        runner = RegressorRunner(name, model, board, member)
        return runner.run()


class TestForecasterForm(forms.Form):
    confirm = forms.BooleanField(label="I want to test this forecaster", required=True)


# Filter forecasters according to model, board, member and what the current user can access
class FilterForecastersForm(forms.Form):
    model = forms.ChoiceField(label=u"Regression model", choices=[], required=False)
    board = forms.ChoiceField(label=u"Board", choices=[], required=False)
    member = forms.ChoiceField(label=u"Members", choices=[], required=False)

    def __init__(self, *args, **kwarsg):
        super(FilterForecastersForm, self).__init__(*args, **kwarsg)
        # Regression model choices
        self.fields["model"].choices = REGRESSION_MODELS
        # Board and members
        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        boards = get_user_boards(current_user)
        members = Member.get_user_team_mates(current_user)
        self.fields["board"].choices = [("", "All")]+[(board.id, board.name) for board in boards]
        self.fields["member"].choices = [("", "None")] + [(member.id, member.external_username) for member in members]

    def get_forecasters(self):
        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        forecasters = Forecaster.get_all_from_member(current_user.member)
        if self.cleaned_data.get("board"):
            forecasters = forecasters.filter(board=self.cleaned_data.get("board"))
        if self.cleaned_data.get("member"):
            forecasters = forecasters.filter(member=self.cleaned_data.get("member"))
        if self.cleaned_data.get("model"):
            forecasters = forecasters.filter(model=self.cleaned_data.get("model"))
        return forecasters.order_by("board", "member", "model")


