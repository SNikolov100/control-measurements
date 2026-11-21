from core.validators import phone_validator, validate_uploaded_image
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as translate
from django.db import models
from core.model_mixins import TextNormalizationMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from .managers import AppUserManager
from .upload_paths import profile_photo_upload_path, person_photo_upload_path
from .validators import validate_username_no_at
from django.db.models.functions import Lower



class AppUser(TextNormalizationMixin, AbstractUser):

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
    email_verified = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=translate('Email verified'),
    )
    email_verification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=translate('Email verification last sent at'),
    )
    first_name = None
    last_name = None
    registration_status = models.CharField(
        max_length=10,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.PENDING,
    )
    person = models.OneToOneField(
        'Person',
        on_delete=models.PROTECT,
        related_name='account',
        null=True,
        blank=True,
        verbose_name=translate('Person'),
    )

    strip_fields = ('username',)
    lowercase_fields = ('email',)
    objects = AppUserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_email_ci_unique",),
            models.CheckConstraint(condition=~models.Q(username__contains="@"), name="accounts_username_no_at",),
        ]


class RegistrationStatusHistory(models.Model):
    class Action(models.TextChoices):
        APPROVE = 'approve', translate('Approve')
        REJECT = 'reject', translate('Reject')
        RECONSIDER = 'reconsider', translate('Reconsider')

    user = models.ForeignKey(
        AppUser,
        on_delete=models.PROTECT,
        related_name='registration_history',
    )
    changed_by = models.ForeignKey(
        AppUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registration_decisions',
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )
    previous_status = models.CharField(
        max_length=10,
        choices=AppUser.RegistrationStatus.choices,
    )
    new_status = models.CharField(
        max_length=10,
        choices=AppUser.RegistrationStatus.choices,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-created_at',)


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


class Person(TextNormalizationMixin, models.Model):
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=translate('First name'),
    )
    middle_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=translate('Middle name'),
    )
    last_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=translate('Last name'),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate('Email'),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_validator],
        verbose_name=translate('Phone'),
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name=translate('Date of birth'),
    )
    address = models.TextField(
        blank=True,
        verbose_name=translate('Address'),
    )
    photo = models.ImageField(
        validators=[validate_uploaded_image],
        blank=True,
        null=True,
        upload_to=person_photo_upload_path,
        verbose_name=translate('Person photo'),
    )
    login_email_reserved = models.BooleanField(
        default=False,
        verbose_name=translate('Login email reserved'),
    )
    lowercase_fields = ('email',)
    strip_fields = ('phone',)
    titlecase_fields = ('first_name', 'middle_name', 'last_name')

    @property
    def is_profile_complete(self):
        return all((value or '').strip() for value in (
                self.first_name,
                self.middle_name,
                self.last_name,
                self.phone,
            )
        )

    def get_full_name(self):
        return ' '.join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    def __str__(self):
        return self.get_full_name() or self.email or f'Person #{self.pk}'


    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('email'),
                condition=models.Q(login_email_reserved=True),
                name='unique_reserved_person_email',
            ),
            models.CheckConstraint(
                condition=(models.Q(login_email_reserved=False) | ~models.Q(email='')),
                name='reserved_person_email_not_empty',
            ),
        ]


