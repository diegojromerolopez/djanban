from crequest.middleware import CrequestMiddleware
from django import forms
from django.core.exceptions import ValidationError

from djangotrellostats.apps.base.auth import get_user_boards
from djangotrellostats.apps.boards.models import Card
from djangotrellostats.apps.forecaster.regression import OLS, GLS, WLS, GLSAR, QuantReg, REGRESSION_MODELS
from djangotrellostats.apps.forecaster.models import Forecaster
from djangotrellostats.apps.members.models import Member


class BuildForecasterForm(forms.ModelForm):
    class Meta:
        model = Forecaster
        fields = ("name", "model", "board", "member")

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
        model = self.instance.model.lower()
        if model == "ols":
            RegressorClass = OLS
        elif model == "gls":
            RegressorClass = GLS
        elif model == "wls":
            RegressorClass = WLS
        elif model == "glsar":
            RegressorClass = GLSAR
        elif model == "quantreg":
            RegressorClass = QuantReg
        else:
            raise ValueError("Invalid RegressorClass")

        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        boards = get_user_boards(current_user)

        board = self.instance.board
        member = self.instance.member

        cards = Card.objects.all()
        if board:
            cards = cards.filter(board=board)
            members = board.members.all()
        elif member:
            cards = cards.filter(members__in=[member])
            members = []
        else:
            cards = cards.filter(board__in=boards)
            members = Member.objects.filter(boards__in=boards).distinct()

        regressor = RegressorClass(member=member, board=board, cards=cards, members=members, forecaster_name=self.instance.name)
        return regressor.run(save=True)


class UpdateForecasterForm(forms.Form):
    confirm = forms.BooleanField(label="I want to update this forecaster", required=True)

    # TODO: unify with BuildForecasterForm
    def save(self, forecaster):
        model = forecaster.model.lower()
        if model == "ols":
            RegressorClass = OLS
        elif model == "gls":
            RegressorClass = GLS
        elif model == "wls":
            RegressorClass = WLS
        elif model == "glsar":
            RegressorClass = GLSAR
        elif model == "quantreg":
            RegressorClass = QuantReg
        else:
            raise ValueError("Invalid RegressorClass")

        current_request = CrequestMiddleware.get_request()
        current_user = current_request.user
        boards = get_user_boards(current_user)

        board = forecaster.board
        member = forecaster.member

        cards = Card.objects.all()
        if board:
            cards = cards.filter(board=board)
            members = board.members.all()
        elif member:
            cards = cards.filter(members__in=[member])
            members = []
        else:
            cards = cards.filter(board__in=boards)
            members = Member.objects.filter(boards__in=boards).distinct()

        regressor = RegressorClass(member=member, board=board, cards=cards, members=members, forecaster_name=forecaster.name)
        regressor.run(save=True)


class TestForecasterForm(forms.Form):
    confirm = forms.BooleanField(label="I want to test this forecaster", required=True)