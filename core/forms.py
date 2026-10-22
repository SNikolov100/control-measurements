from django import forms
from .models import Specialty, CompanySettings, SystemSettings

class SpecialtyBaseForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = "__all__"

class SpecialtyCreateForm(SpecialtyBaseForm):
    ...

class SpecialtyEditForm(SpecialtyBaseForm):
    ...

class SpecialtyDeleteForm(SpecialtyBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = "__all__"


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = "__all__"
