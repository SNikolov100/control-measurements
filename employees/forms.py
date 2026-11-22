from django import forms
from core.validators import validate_uploaded_image, phone_validator
from .models import Employee
from django.contrib.auth.models import Group
from .choices import EmployeeRequestAction, PersonNameSource, PersonPhoneSource
from django.utils.translation import gettext_lazy as translate

class EmployeeBaseForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=30,
        required=False,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={'placeholder': translate('For example: +359 888 123 456'), 'autocomplete': 'tel'}),
        label=translate('Phone'),
        help_text=translate('Enter a contact phone number.'),
    )
    email = forms.EmailField(
        max_length=254,
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': translate('For example: employee@example.com'), 'autocomplete': 'email'}),
        label=translate('Email'),
        help_text=translate('Enter a valid email address.'),
        error_messages={'invalid': translate('Enter a valid email address.')},
    )
    photo = forms.ImageField(
        required=False,
        validators=[validate_uploaded_image],
        widget=forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
        label=translate('Employee photo'),
        help_text=translate('Upload a JPEG, PNG, or WebP photo up to 5 MB. The photo is optional.'),
        error_messages={'invalid_image': translate('Upload a valid JPEG, PNG, or WebP image.')},
    )

    class Meta:
        model = Employee
        fields = ('position', 'phone', 'email', 'photo', 'notes', 'specialties')
        widgets = {
            'position': forms.TextInput(
                attrs={'placeholder': translate('For example: Laboratory technician')},
            ),
            'notes': forms.Textarea(
                attrs={'rows': 5, 'placeholder': translate('Add relevant information about the employee.')},
            ),
            'specialties': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'position': translate("Enter the employee's position or work role."),
            'notes': translate('Optional additional information.'),
            'specialties': translate('Select one or more specialties in which the employee is qualified to work.'),
        }
        error_messages = {
            'email': {'invalid': translate('Enter a valid email address.')},
        }

class EmployeeCreateForm(EmployeeBaseForm):
    first_name = forms.CharField(
        max_length=30,
        label=translate('First name'),
        widget=forms.TextInput(attrs={'placeholder': translate('Enter first name'), 'autocomplete': 'given-name'}),
        help_text=translate("Enter the employee's first name."),
        error_messages={'required': translate('Enter the first name.')},
    )
    middle_name = forms.CharField(
        max_length=30,
        label=translate('Middle name'),
        widget=forms.TextInput(attrs={'placeholder': translate('Enter middle name'), 'autocomplete': 'additional-name'}),
        help_text=translate("Enter the employee's middle name."),
        error_messages={'required': translate('Enter the middle name.')},
    )
    last_name = forms.CharField(
        max_length=30,
        label=translate('Last name'),
        widget=forms.TextInput(attrs={'placeholder': translate('Enter last name'), 'autocomplete': 'family-name'}),
        help_text=translate("Enter the employee's last name."),
        error_messages={'required': translate('Enter the last name.')},
    )

    class Meta(EmployeeBaseForm.Meta):
        fields = (
            'first_name',
            'middle_name',
            'last_name',
            'position',
            'phone',
            'email',
            'photo',
            'notes',
            'specialties',
        )

class EmployeeEditForm(EmployeeCreateForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk and self.instance.person_id:
            person = self.instance.person
            personal_fields = ('first_name', 'middle_name', 'last_name', 'phone', 'email', 'photo')

            for field in personal_fields:
                self.initial[field] = getattr(person, field)

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



class EmployeeRequestReviewForm(forms.Form):
    action = forms.ChoiceField(
        choices=EmployeeRequestAction.choices,
        widget=forms.RadioSelect,
        label=translate('Decision'),
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        label=translate('Existing employee'),
    )
    role = forms.ModelChoiceField(
        queryset=Group.objects.order_by('name'),
        required=False,
        label=translate('Permission group'),
    )
    review_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=translate('Review note'),
    )
    name_source = forms.ChoiceField(
        choices=PersonNameSource.choices,
        widget=forms.RadioSelect,
        required=False,
        label=translate('Choose which names to keep'),
    )
    phone_source = forms.ChoiceField(
        choices=PersonPhoneSource.choices,
        widget=forms.RadioSelect,
        required=False,
        label=translate('Choose which phone number to keep'),
    )
    confirm_name_difference = forms.BooleanField(
        required=False,
        label=translate('I confirm that the different names refer to the same person.'),
        help_text=translate('Confirm that both records belong to the same person. Then choose which names to keep.')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = (Employee.objects
            .filter(user__isnull=True, is_active=True)
            .order_by('person__first_name', 'person__middle_name', 'person__last_name')
        )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        employee = cleaned_data.get('employee')
        role = cleaned_data.get('role')
        note = cleaned_data.get('review_note', '')

        if action != EmployeeRequestAction.LINK:
            cleaned_data['employee'] = None
            cleaned_data['name_source'] = None
            cleaned_data['phone_source'] = None

        if action == EmployeeRequestAction.LINK and not employee:
            self.add_error('employee', translate('Select an existing employee.'),)

        if action in {EmployeeRequestAction.LINK, EmployeeRequestAction.CREATE,} and not role:
            self.add_error('role', translate('Select a user role.'),)

        if action == EmployeeRequestAction.REJECT and not note.strip():
            self.add_error('review_note', translate('Enter a reason for rejection.'),)

        return cleaned_data
