from django import forms
from .models import Specialty

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = "__all__"

class SpecialtyCreateForm(SpecialtyForm):
    ...

class SpecialtyEditForm(SpecialtyForm):
    ...

class SpecialtyDeleteForm(SpecialtyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True
