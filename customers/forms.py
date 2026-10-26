from django import forms
from django.utils.translation import gettext_lazy as translate
from core.base_forms import DeleteConfirmationForm
from .models import Customer, CustomerSite, CustomerContact

class CustomerBaseForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = (
            'company_name',
            'short_name',
            'country',
            'city',
            'address',
            'phone',
            'email',
            'notes',
            'is_active',
        )
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'placeholder': translate('For example: +359 32 123 456'),
                    'autocomplete': 'tel',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': translate('For example: office@example.com'),
                    'autocomplete': 'email',
                },
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': translate('Add relevant information about the customer.')
                },
            ),
        }
        help_texts = {
            'phone': translate('Enter the main customer phone number.'),
            'email': translate('Enter the main customer email address.'),
            "notes": translate('Optional additional information.')
        }
        error_messages = {
            'company_name': {
                'required': translate("Enter the customer's company name."),
                'unique': translate('A customer with this company name already exists.'),
            },
            'short_name': {
                'required': translate('Enter a short name for the customer.'),
                'unique': translate('A customer with this short name already exists.'),
            },
            'email': {'invalid': translate('Enter a valid customer email address.'),},
        }


class CustomerCreateForm(CustomerBaseForm):
    ...

class CustomerEditForm(CustomerBaseForm):
    ...

class CustomerSiteBaseForm(forms.ModelForm):
    class Meta:
        model = CustomerSite
        fields = (
            'name',
            'short_name',
            'city',
            'address',
            'phone',
            'email',
            'is_active',
        )
        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'placeholder': translate('For example: +359 32 123 456'),
                    'autocomplete': 'tel',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': translate('For example: site@example.com'),
                    'autocomplete': 'email',
                },
            ),
        }
        help_texts = {
            'name': translate('Enter the official name of the customer site.'),
            'short_name': translate('Enter a shorter name for lists and navigation.'),
        }
        error_messages = {
            'name': {'required': translate('Enter the customer-site name.')},
            'email': {'invalid': translate('Enter a valid customer-site email address.')},
        }


class CustomerSiteCreateForm(CustomerSiteBaseForm):
    ...

class CustomerSiteEditForm(CustomerSiteBaseForm):
    ...

class CustomerContactBaseForm(forms.ModelForm):
    class Meta:
        model = CustomerContact
        fields = (
            'full_name',
            'position',
            'phone',
            'email',
            'photo',
            'notes',
            'is_primary',
            'is_active',
        )
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'For example: Ivan Ivanov',
                    'autocomplete': 'name',},
            ),
            'position': forms.TextInput(
                attrs={'placeholder': 'For example: Technical manager'},
            ),
            'phone': forms.TextInput(
                attrs={
                    'placeholder': 'For example: +359 888 123 456',
                    'autocomplete': 'tel',
                },
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'For example: contact@example.com',
                    'autocomplete': 'email',
                },
            ),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp'}),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Add relevant information about the responsible contact.',
                },
            ),
        }
        error_messages = {
            'full_name': {'required': translate("Enter the responsible contact's full name.")},
            'email': {'invalid': translate('Enter a valid contact email address.')},
            'photo': {'invalid_image': translate('Upload a valid JPEG, PNG, or WebP image.')},
        }

    def __init__(self, *args, site=None, **kwargs):
        super().__init__(*args, **kwargs)

        if site is not None:
            self.instance.site = site

class CustomerContactCreateForm(CustomerContactBaseForm):
    ...

class CustomerContactEditForm(CustomerContactBaseForm):
    ...
class CustomerContactDeleteForm(DeleteConfirmationForm):
    ...