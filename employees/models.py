from django.db import models, transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as translate
from core.model_mixins import AutoSlugMixin, TimestampMixin, TextNormalizationMixin
from core.validators import phone_validator


class Employee(TextNormalizationMixin, AutoSlugMixin, TimestampMixin):
    strip_fields = ('full_name', 'position', 'phone', 'email', 'notes',)
    lowercase_fields = ('email',)
    titlecase_fields = ('full_name',)

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

    def _change_activity_status(self, *, is_active,event_type, description="",):
        if self.is_active == is_active:
            return False

        with transaction.atomic():
            self.is_active = is_active
            self.save(update_fields={'is_active'})
            EmployeeHistory.objects.create(
                employee=self,
                event_type=event_type,
                description=description,
            )

        return True

    def activate(self, description=""):
        return self._change_activity_status(
            is_active=True,
            event_type=EmployeeHistory.EventType.ACTIVATED,
            description=description,
        )

    def deactivate(self, description=""):
        return self._change_activity_status(
            is_active=False,
            event_type=EmployeeHistory.EventType.DEACTIVATED,
            description=description,
        )

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