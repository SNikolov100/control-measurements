from django.db import models, transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as translate
from core.model_mixins import AutoSlugMixin, TimestampMixin, TextNormalizationMixin
from core.validators import phone_validator, validate_uploaded_image
from pathlib import Path
from uuid import uuid4
from django.conf import settings
from .choices import EmployeeHistoryEventType, EmployeeRequestStatus


class Employee(TextNormalizationMixin, AutoSlugMixin, TimestampMixin):
    strip_fields = ('position', 'notes',)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='employee',
        null=True,
        blank=True,
        verbose_name=translate('User account'),
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=translate('Position'),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate('Notes'),
    )
    specialties = models.ManyToManyField(
        'core.Specialty',
        blank=True,
        related_name='employees',
        verbose_name=translate('Specialties'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=translate('Active'),
    )
    person = models.OneToOneField(
        'accounts.Person',
        on_delete=models.PROTECT,
        related_name='employee',
        null=False,
        blank=False,
        verbose_name=translate('Person'),
    )

    @property
    def full_name(self):
        return self.person.get_full_name()

    @property
    def phone(self):
        return self.person.phone

    @property
    def email(self):
        return self.person.email

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
        return f'{self.pk}-{name_slug}'

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ('person__first_name', 'person__middle_name', 'person__last_name')
        verbose_name = translate('Employee')
        verbose_name_plural = translate('Employees')

class EmployeeHistory(models.Model):
    EventType = EmployeeHistoryEventType

    employee = models.ForeignKey(
        'Employee',
        on_delete=models.PROTECT,
        related_name='history',
        verbose_name=translate('Employee'),
    )
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        verbose_name=translate('Event type'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=translate('Description'),
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=translate('Changed at'),
    )

    def __str__(self):
        return f'{self.employee} - {self.get_event_type_display()}'

    class Meta:
        ordering = ('-changed_at',)
        verbose_name = translate('Employee history')
        verbose_name_plural = translate('Employee histories')



class EmployeeRequest(models.Model):
    Status = EmployeeRequestStatus

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='employee_requests',
        verbose_name=translate('User'),
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.PROTECT,
        related_name='account_requests',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reviewed_employee_requests',
        null=True,
        blank=True,
    )
    review_note = models.TextField(
        blank=True,
    )
    reconsidered_from = models.OneToOneField(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='reconsidered_as',
    )
    reconsidered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reconsidered_employee_requests',
    )
    reconsideration_note = models.TextField(
        blank=True,
    )

    def __str__(self):
        return f'{self.user} - {self.get_status_display()}'

    class Meta:
        ordering = ('-created_at',)
        constraints = [models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='pending'),
                name='unique_pending_employee_req',
            ),
        ]
