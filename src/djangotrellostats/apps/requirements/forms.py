import shortuuid

from djangotrellostats.apps.requirements.models import Requirement
from django import forms


# Requirement form
class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ["code", "name", "description", "value"]


# Requirement form
class NewRequirementForm(RequirementForm):
    class Meta:
        model = Requirement
        fields = ["code", "name", "description", "value"]

    def __init__(self, *args, **kwargs):
        super(NewRequirementForm, self).__init__(*args, **kwargs)
        self.initial["code"] = u"{0}{1}".format(self.instance.board.name[0].upper(),
                                                shortuuid.ShortUUID().random(length=4).upper())
        #self.fields["descritpion"].widget =


# Requirement form
class EditRequirementForm(RequirementForm):
    class Meta:
        model = Requirement
        fields = ["name", "description", "value"]


# Requirement form
class DeleteRequirementForm(forms.Form):
    confirmed = forms.BooleanField(label=u"Confirm you want to delete this requirement")
