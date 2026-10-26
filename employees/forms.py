from django import forms
from .models import Employee
from django.utils.translation import gettext_lazy as translate

class EmployeeBaseForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = (
            'full_name',
            'position',
            'phone',
            'email',
            'photo',
            'notes',
            'specialties',
        )
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'For example: Ivan Ivanov',
                    'autocomplete': 'name',
                },
            ),
            'position': forms.TextInput(
                attrs={'placeholder': 'For example: Laboratory technician'},
            ),
            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'For example: +359 888 123 456',
                    'autocomplete': 'tel',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'For example: employee@example.com',
                    'autocomplete': 'email',
                },
            ),
            'photo': forms.ClearableFileInput(
                attrs={
                    "accept": 'image/jpeg,image/png,image/webp',
                },
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Add relevant information about the employee.',
                },
            ),
            'specialties': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'full_name': translate("Enter the employee's full name."),
            'position': translate("Enter the employee's position or work role."),
            'phone': translate('Enter a contact phone number.'),
            'email': translate('Enter a valid email address.'),
            'photo': translate('Upload a JPEG, PNG, or WebP photo up to 5 MB. The photo is optional.'),
            'notes': translate('Optional additional information.'),
            'specialties': translate('Select one or more specialties in which the employee is qualified to work.'),
        }
        error_messages = {
            'full_name': {'required': translate("Enter the employee's full name.")},
            'email': {'invalid': translate('Enter a valid email address.')},
            'photo': {'invalid_image': translate('Upload a valid JPEG, PNG, or WebP image.'),
            },
        }

class EmployeeCreateForm(EmployeeBaseForm):
    ...

class EmployeeEditForm(EmployeeBaseForm):
    ...

class EmployeeActivityStatusForm(forms.Form):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': translate("Enter the reason for changing the employee's active status."),
            },
        ),
        label= translate('Reason'),
        help_text= translate('Enter the reason for activating or deactivating the employee.'),
        error_messages={'required': translate("Enter the reason for changing the employee's active status."),}
    )
