from django import forms
from .models import Specialty, CompanySettings, SystemSettings
from .base_forms import DeleteConfirmationForm

class SpecialtyBaseForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = "__all__"

class SpecialtyCreateForm(SpecialtyBaseForm):
    ...

class SpecialtyEditForm(SpecialtyBaseForm):
    ...

class SpecialtyDeleteForm(DeleteConfirmationForm):
    ...

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = "__all__"


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = "__all__"
