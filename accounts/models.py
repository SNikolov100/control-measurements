from pathlib import Path
from uuid import uuid4
from core.validators import phone_validator, validate_uploaded_image
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as translate
from django.db import models
from core.model_mixins import TextNormalizationMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from .validators import validate_username_no_at
from django.db.models.functions import Lower

def profile_photo_upload_path(instance, filename):
    file_extension = Path(filename).suffix.lower()
    return f'profiles/{uuid4().hex}{file_extension}'


class AppUser(TextNormalizationMixin, AbstractUser):
    strip_fields = ('username',)
    lowercase_fields = ('email',)

    class RegistrationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    username = models.CharField(
        max_length=50,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username_no_at],
        help_text=translate('50 characters or fewer. Letters, digits and ./+/-/_ only.'),
        error_messages={'unique': translate('A user with that username already exists.')},
        verbose_name=translate('Username'),
    )
    email = models.EmailField(
        verbose_name=translate('Email address'),
    )
    first_name = None
    last_name = None
    registration_status = models.CharField(
        max_length=10,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_email_ci_unique",),
            models.CheckConstraint(condition=~models.Q(username__contains="@"), name="accounts_username_no_at",),
        ]


class Profile(TextNormalizationMixin, models.Model):
    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    first_name = models.CharField(
        max_length=30,
        blank=False,
        verbose_name=translate('First name'),
    )
    middle_name = models.CharField(
        max_length=30,
        blank=False,
        verbose_name=translate('Middle name'),
    )
    last_name = models.CharField(
        max_length=30,
        blank=False,
        verbose_name=translate('Last name'),
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=30,
        blank=False,
        validators=[phone_validator],
        verbose_name=translate('Phone'),
    )
    address = models.TextField(
        blank=True,
        verbose_name=translate('Address'),
    )
    photo = models.ImageField(
        upload_to=profile_photo_upload_path,
        validators=[validate_uploaded_image],
        blank=True,
        null=True,
        verbose_name=translate('Profile photo'),
    )
    titlecase_fields = ('first_name','middle_name', 'last_name')

    def get_full_name(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name,]))

    def __str__(self):
        return self.get_full_name()


