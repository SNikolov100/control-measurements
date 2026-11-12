from django.contrib.auth import get_user_model
from django.contrib.auth.forms import BaseUserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as translate
from uuid import uuid4

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
            email = email.strip().lower()
            if AppUser.objects.filter(email__iexact=email).exists():
                self.add_error('email', translate('This email is already registered.'))
            cleaned_data['email'] = email

        if username:
            username = username.strip().lower()
            if AppUser.objects.filter(username__iexact=username).exists():
                self.add_error('username', translate('This username is already taken.'))
            cleaned_data['username'] = username

        return cleaned_data


    def save(self, commit=True):
        user = super().save(commit=False)

        if not user.username:
            user.username = f"user_{uuid4().hex}"

        user.registration_status = AppUser.RegistrationStatus.PENDING

        if commit:
            user.save()

        return user



