from django import forms
from .models import Employee, EmployeeHistory

class EmployeeBaseForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

class EmployeeCreateForm(EmployeeBaseForm):
    ...

class EmployeeEditForm(EmployeeBaseForm):
    class Meta(EmployeeBaseForm.Meta):
        exclude = ("is_active",)

class EmployeeActivityStatusForm(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea,
        label="Reason",
        help_text="Enter the reason for activating or deactivating the employee.",
    )