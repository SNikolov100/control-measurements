from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as translate

from core.model_mixins import AutoSlugMixin, TimestampMixin
from core.validators import phone_validator

class Employee(AutoSlugMixin, TimestampMixin):
    full_name = models.CharField(
        max_length=100,
        verbose_name=translate('Full name'),
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=translate('Position'),
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
    specialties = models.ManyToManyField(
        "core.Specialty",
        blank=True,
        related_name="employees",
        verbose_name=translate("Specialties"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active'),
    )

    def normalize_fields(self):
        if self.full_name:
            self.full_name = " ".join(self.full_name.split()).title()

        if self.position:
            self.position = " ".join(self.position.split())

        if self.phone:
            self.phone = self.phone.strip()

        if self.email:
            self.email = self.email.strip()

    def clean_fields(self, exclude=None):
        self.normalize_fields()
        super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        self.normalize_fields()
        super().save(*args, **kwargs)

    def build_slug(self):
        name_slug = slugify(self.full_name,allow_unicode=True,)
        return f"{self.pk}-{name_slug}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ("full_name",)
        verbose_name = translate("Employee")
        verbose_name_plural = translate("Employees")

class EmployeeHistory(models.Model):
    class EventType(models.TextChoices):
        CREATED = "created", translate("Created")
        UPDATED = "updated", translate("Updated")
        SPECIALTY_ADDED = ("specialty_added",translate("Specialty added"),)
        SPECIALTY_REMOVED = ("specialty_removed",translate("Specialty removed"),)
        ACTIVATED = "activated", translate("Activated")
        DEACTIVATED = "deactivated", translate("Deactivated")

    employee = models.ForeignKey(
        "Employee",
        on_delete=models.PROTECT,
        related_name="history",
        verbose_name=translate("Employee"),
    )
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        verbose_name=translate("Event type"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=translate("Description"),
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate("Changed at"),
    )

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.get_event_type_display()}"
        )

    class Meta:
        ordering = ("-changed_at",)
        verbose_name = translate("Employee history")
        verbose_name_plural = translate("Employee histories")