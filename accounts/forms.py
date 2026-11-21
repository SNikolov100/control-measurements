from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as translate
from uuid import uuid4
from accounts.models import Profile, Person
from django.contrib.auth.forms import AuthenticationForm

AppUser = get_user_model()

class AppUserRegistrationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': translate('Enter your email')}),
    )
    username = forms.CharField(
        max_length=50,
        required=False,
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': translate('Enter your username')}),
    )

    class Meta:
        model = AppUser
        fields = ('email', 'username', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip().lower()
        username = (cleaned_data.get('username') or '').strip().lower()
        cleaned_data['email'] = email
        cleaned_data['username'] = username

        if email:
            if (AppUser.objects.filter(email__iexact=email).exists()
                    or
                Person.objects.filter(email__iexact=email, login_email_reserved=True).exists()):
                self.add_error('email', translate('This email is already registered.'))

        if username:
            if "@" in username:
                self.add_error('username', translate("Username cannot contain '@'."))

            elif AppUser.objects.filter(username__iexact=username).exists():
                self.add_error('username', translate('This username is already taken.'))

        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.username:
            user.username = f"user_{uuid4().hex}"

        user.registration_status = AppUser.RegistrationStatus.PENDING

        if commit:
            user.save()

        return user

class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('first_name', 'middle_name', 'last_name', 'phone'):
            self.fields[field_name].required = True

    class Meta:
        model = Person
        fields = (
            'first_name',
            'middle_name',
            'last_name',
            'phone',
            'date_of_birth',
            'address',
            'photo',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'middle_name': forms.TextInput(attrs={'autocomplete': 'additional-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'phone': forms.TextInput(attrs={
                    'placeholder': '+359 888 123 456',
                    'autocomplete': 'tel',
                }
            ),
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'autocomplete': 'bday'},
                format="%Y-%m-%d"
            ),
            'address': forms.Textarea(attrs={'autocomplete': 'street-address'}),
        }

        error_messages = {
            'first_name': {'required': translate('Enter your first name.')},
            'middle_name': {'required': translate('Enter your middle name.')},
            'last_name': {'required': translate('Enter your last name.')},
            'phone': {'required': translate('Enter your phone number.')},
        }

class AppUserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=translate("Email or username"),
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )