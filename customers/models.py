from django.db import models
from django.utils.translation import gettext_lazy as translate
from core.model_mixins import CompanyMixin, TimestampMixin, AutoSlugMixin
from django.core.exceptions import ValidationError
from core.validators import phone_validator


class Customer(AutoSlugMixin, CompanyMixin, TimestampMixin):
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate("Active")
    )

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ("company_name",)
        verbose_name = translate("Customer")
        verbose_name_plural = translate("Customers")

class CustomerSite(AutoSlugMixin, TimestampMixin):
    customer=models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT,
        related_name='sites',
    )
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=translate("Name"),
    )
    short_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=translate("Short name"),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_validator],
        verbose_name=translate("Phone"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate("Email"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate("Notes")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate("Active"),
    )

    def __str__(self):
        return f"{self.customer.short_name} - {self.short_name}"

    class Meta:
        ordering = ('customer__company_name', 'name')
        verbose_name =translate('Customer site')
        verbose_name_plural=translate('Customer sites')


class CustomerContact(TimestampMixin):
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
        verbose_name=translate("Phone"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate("Email"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate("Notes"),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=translate("Primary contact"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate("Active"),
    )

    def clean(self):
        super().clean()
        errors = {}
        duplicate_contacts = type(self).objects.none()

        if self.site_id and self.full_name:
            duplicate_contacts = (
                type(self)
                .objects.
                filter(site_id=self.site_id,full_name__iexact=self.full_name.strip())
                .exclude(pk=self.pk)
            )

        if self.phone and duplicate_contacts.filter(phone=self.phone.strip(),).exists():
            errors["phone"] = translate("A contact with the same name and phone number already exists for this customer site.")

        if self.email and duplicate_contacts.filter(email__iexact=self.email.strip(),).exists():
            errors["email"] = translate("A contact with the same name and email address already exists for this customer site.")

        if self.is_primary and not self.is_active:
            errors["is_primary"] = translate("An inactive contact cannot be the primary contact.")

        if self.is_primary and self.is_active and self.site_id:
            another_primary_contact_exists = (
                type(self).objects
                .filter(
                    site_id=self.site_id,
                    is_primary=True,
                    is_active=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )

            if another_primary_contact_exists:
                errors["is_primary"] = translate("This customer site already has an active primary contact.")

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.site.customer.short_name} - {self.site.short_name} - {self.full_name}")

    class Meta:
        ordering = ("site__customer__company_name",
                    "site__name",
                    "-is_primary",
                    "full_name"
                    )
        verbose_name = translate("Customer contact")
        verbose_name_plural = translate("Customer contacts")
