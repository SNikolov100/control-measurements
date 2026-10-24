from django.db import models
from django.utils.translation import gettext_lazy as translate
from core.model_mixins import CompanyMixin, TimestampMixin, AutoSlugMixin, TextNormalizationMixin
from django.core.exceptions import ValidationError
from core.validators import phone_validator


class Customer(TextNormalizationMixin, AutoSlugMixin, CompanyMixin, TimestampMixin):
    strip_fields = ('company_name', 'short_name', 'city', 'country', 'address', 'phone', 'email', 'notes',)
    lowercase_fields = ('email',)
    default_text_values = {"country": "Bulgaria",}

    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active')
    )

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ('company_name',)
        verbose_name = translate('Customer')
        verbose_name_plural = translate('Customers')

class CustomerSite(TextNormalizationMixin, AutoSlugMixin, TimestampMixin):
    strip_fields = ('name','short_name','city','address','phone','email',)
    lowercase_fields = ('email',)
    customer=models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT,
        related_name='sites',
    )
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=translate('Name'),
    )
    short_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=translate('Short name'),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=translate('City'),
        help_text=translate("Leave blank to use the customer's city."),
        error_messages={'max_length': translate('The city cannot contain more than 100 characters.')},
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=translate('Address'),
        help_text=translate("Leave blank to use the customer's address."),
        error_messages={'max_length': translate('The address cannot contain more than 255 characters.')},
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_validator],
        verbose_name=translate('Phone'),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate('Email'),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate('Notes')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active'),
    )

    @property
    def effective_city(self):
        return self.city or self.customer.city

    @property
    def effective_address(self):
        return self.address or self.customer.address

    def __str__(self):
        return f"{self.customer.short_name} - {self.short_name}"

    class Meta:
        ordering = ('customer__company_name', 'name')
        verbose_name =translate('Customer site')
        verbose_name_plural=translate('Customer sites')


class CustomerContact(TextNormalizationMixin, TimestampMixin):
    strip_fields = ('full_name', 'position', 'phone', 'email', 'notes',)
    lowercase_fields = ('email',)
    titlecase_fields = ('full_name',)

    site = models.ForeignKey(
        'CustomerSite',
        on_delete=models.PROTECT,
        related_name="contacts",
        verbose_name=translate("Customer site"),
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name=translate("Full name"),
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=translate("Position"),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_validator],
        verbose_name=translate('Phone'),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate('Email'),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate('Notes'),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=translate('Primary contact'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active'),
    )

    def clean(self):
        super().clean()
        errors = {}
        duplicate_contacts = type(self).objects.none()

        if self.site_id and self.full_name:
            duplicate_contacts = (type(self)
                .objects.
                filter(site_id=self.site_id,full_name__iexact=self.full_name)
                .exclude(pk=self.pk)
            )

        if self.phone and duplicate_contacts.filter(phone=self.phone,).exists():
            errors['phone'] = translate('A contact with the same name and phone number already exists for this customer site.')

        if self.email and duplicate_contacts.filter(email__iexact=self.email,).exists():
            errors['email'] = translate('A contact with the same name and email address already exists for this customer site.')

        if self.is_primary and not self.is_active:
            errors['is_primary'] = translate('An inactive contact cannot be the primary contact.')

        if self.is_primary and self.is_active and self.site_id:
            another_primary_contact_exists = (type(self).objects
                .filter(
                    site_id=self.site_id,
                    is_primary=True,
                    is_active=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )

            if another_primary_contact_exists:
                errors['is_primary'] = translate('This customer site already has an active primary contact.')

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.site.customer.short_name} - {self.site.short_name} - {self.full_name}")

    class Meta:
        ordering = ('site__customer__company_name', 'site__name', '-is_primary', 'full_name')
        verbose_name = translate("Customer contact")
        verbose_name_plural = translate("Customer contacts")
