from django import forms
from .models import Specialty, CompanySettings, SystemSettings
from .base_forms import DeleteConfirmationForm
from django.utils.translation import gettext_lazy as translate

class SpecialtyBaseForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = (
            'code',
            'name',
            'short_name',
            'description',
            'color',
            'sort_order',
            'is_active',
        )
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "For example: Electrical measurements",},
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe the specialty and its typical applications.",
                },
            ),
            "color": forms.TextInput(attrs={"type": "color"}),
            "sort_order": forms.NumberInput(
                attrs={
                    "min": 0,
                    "placeholder": "For example: 10",
                },
            ),
        }
        help_texts = {
            "code": translate("Enter a unique code. It will be stored in uppercase."),
            "name": translate("Enter the full specialty name."),
            "short_name": translate("Enter a shorter name for lists and badges."),
            "description": translate("Optional additional information."),
            "color": translate("Select the color used for visual identification."),
            "sort_order": translate("Lower values are displayed first."),
            "is_active": translate("Inactive specialties remain visible but should not be used for new equipment types or employees."),
        }
        error_messages = {
            "code": {
                "required": translate("Enter a code for the specialty."),
                "unique": translate("A specialty with this code already exists."),
            },
            "name": {
                "required": translate("Enter the specialty name."),
                "unique": translate("A specialty with this name already exists."),
            },
            "color": {"required": translate("Select a color for the specialty.")},
            "sort_order": {"invalid": translate("Enter a valid non-negative sort order.")},
        }

class SpecialtyCreateForm(SpecialtyBaseForm):
    ...

class SpecialtyEditForm(SpecialtyBaseForm):
    ...

class SpecialtyDeleteForm(DeleteConfirmationForm):
    ...

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = (
            'company_name',
            'short_name',
            'country',
            'city',
            'address',
            'phone',
            'email',
            'notes',
        )
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'For example: +359 32 123 456',
                    'autocomplete': 'tel',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'For example: office@example.com',
                    'autocomplete': 'email',
                },
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Add relevant information about the operating company.',
                },
            ),
        }
        help_texts = {
            'company_name': translate('Enter the official name of the company operating the system.'),
            'short_name': translate('Enter a shorter name for lists, documents, and navigation.'),
            'country': translate('Leave empty to use Bulgaria.'),
            'city': translate("Enter the company's main city."),
            'address': translate("Enter the company's main address."),
            'phone': translate("Enter the company's main phone number."),
            'email': translate("Enter the company's main email address."),
            'notes': translate('Optional additional company information.'),
        }
        error_messages = {
            'company_name': {
                'required': translate('Enter the company name.'),
            },
            'short_name': {
                'required': translate('Enter the company short name.'),
            },
            'email': {'invalid': translate('Enter a valid company email address.')},
        }


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = (
            'default_calendar_period',
            'show_weekends',
            'workday_start',
            'workday_end',
            'warning_days_before_due',
            'critical_days_before_due',
            'show_overdue_alerts',
            'auto_create_next_inspection',
            'require_assigned_employee_before_start',
            'require_result_before_completion',
        )
        widgets = {
            'workday_start': forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M',
            ),
            "workday_end": forms.TimeInput(
                attrs={'type': 'time',},
                format='%H:%M',
            ),
            "warning_days_before_due": forms.NumberInput(
                attrs={
                    'min': 0,
                    'placeholder': 'For example: 14',
                },
            ),
            "critical_days_before_due": forms.NumberInput(
                attrs={
                    'min': 0,
                    'placeholder': 'For example: 3',
                },
            ),
        }
        help_texts = {
            'default_calendar_period': translate('Select the default period displayed in the calendar.'),
            'show_weekends': translate('Include Saturday and Sunday in the calendar.'),
            'workday_start': translate('Select the normal start of the working day.'),
            'workday_end': translate('Select the normal end of the working day.'),
            'warning_days_before_due': translate('Number of days before a due date when a warning should be displayed.'),
            'critical_days_before_due': translate('Number of days before a due date when the warning becomes critical.'),
            'show_overdue_alerts': translate('Display alerts for overdue activities.'),
            'auto_create_next_inspection': translate('Automatically prepare the next inspection after successful completion.'),
            'require_assigned_employee_before_start': translate('Prevent an activity from starting without an assigned employee.'),
            'require_result_before_completion': translate('Prevent an inspection from being completed without a result.'),
        }
        error_messages = {
            'default_calendar_period': {'required': translate('Select the default calendar period.')},
            'workday_start': {
                'required': translate('Enter the start of the working day.'),
                'invalid': translate('Enter a valid workday start time.'),
            },
            'workday_end': {
                'required': translate('Enter the end of the working day.'),
                'invalid': translate('Enter a valid workday end time.'),
            },
            'warning_days_before_due': {
                'required': translate('Enter the warning period in days.'),
                'invalid': translate('Enter a valid non-negative number of days.'),
            },
            'critical_days_before_due': {
                'required': translate('Enter the critical period in days.'),
                'invalid': translate('Enter a valid non-negative number of days.'),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['workday_start'].input_formats = ['%H:%M']
        self.fields['workday_end'].input_formats = ['%H:%M']
