from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as translate
from core.validators import phone_validator


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate("Created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=translate("Updated at"),
    )

    class Meta:
        abstract = True


class SingleRecordMixin(models.Model):
    def clean(self):
        super().clean()
        model_class = type(self)

        if model_class.objects.exclude(pk=self.pk).exists():
            raise ValidationError(translate("Only one record of this type is allowed."))

    class Meta:
        abstract = True


class CompanyMixin(models.Model):
    company_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=translate('Company name'),
    )
    short_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=translate('Short name'),
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=translate('City'),
    )
    country = models.CharField(
        max_length=50,
        blank=True,
        default="Bulgaria",
        verbose_name=translate('Country'),
    )
    address = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=translate("Address"),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        validators=[phone_validator],
        verbose_name=translate("Phone"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=translate('Email'),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate("Notes"),
    )

    class Meta:
        abstract = True


class AutoSlugMixin(models.Model):
    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        editable=False,
        allow_unicode=True,
        verbose_name=translate("Slug"),
    )

    def build_slug(self):
        return f"{self.pk}-{slugify(self.short_name, allow_unicode=True)}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.slug = self.build_slug()
            update_fields = kwargs.get("update_fields")

            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"slug"}
            super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)
        self.slug = self.build_slug()
        type(self).objects.filter(pk=self.pk).update(slug=self.slug)


    class Meta:
        abstract = True