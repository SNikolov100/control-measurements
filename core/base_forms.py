from django import forms
from django.utils.translation import gettext_lazy as translate

class DeleteConfirmationForm(forms.Form):
    confirm = forms.BooleanField(
        label=translate("I confirm that I want to delete this record."),
        error_messages={
            "required": translate("You must confirm the deletion before continuing."),},
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("instance", None)
        super().__init__(*args, **kwargs)