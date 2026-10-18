from django.core.exceptions import ValidationError
from django.db import models
from .base_models import TimestampMixin, SingleRecordMixin
from django.utils.translation import gettext_lazy as translate
from .validators import hex_color_validator, phone_validator
from datetime import time

class Specialty(TimestampMixin):

    code = models.CharField(
        max_length = 20,
        unique=True,
        verbose_name = translate('Code'),
    )
    name = models.CharField(
        max_length = 150,
        unique = True,
        verbose_name = translate('Name'),
    )
    short_name = models.CharField(
        max_length = 50,
        blank = True,
        verbose_name = translate('Short name'),
    )
    description = models.TextField(
        blank = True,
        verbose_name = translate('Description'),
    )
    color = models.CharField(
        max_length = 7,
        default = '#2878C8',
        validators = [hex_color_validator],
        verbose_name = translate('Color'),
    )
    sort_order = models.PositiveIntegerField(
        default = 0,
        verbose_name = translate("Sort order"),
    )
    is_active = models.BooleanField(
        default = True,
        verbose_name = translate("Active"),
    )

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.strip().upper()
        if self.color:
            self.color = self.color.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = translate("Speciality")
        verbose_name_plural = translate("Specialities")

class CompanySettings(TimestampMixin, SingleRecordMixin):
    company_name = models.CharField(
        max_length = 100,
        verbose_name = translate('Company name'),
    )
    short_name = models.CharField(
        max_length = 50,
        blank = True,
        verbose_name = translate('Short name'),
    )
    city = models.CharField(
        max_length = 50,
        blank = True,
        verbose_name = translate('City'),
    )
    country = models.CharField(
        max_length = 50,
        blank = True,
        default = "Bulgaria",
        verbose_name = translate('Country'),
    )
    phone = models.CharField(
        max_length = 30,
        blank = True,
        validators = [phone_validator],
        verbose_name = translate("Phone"),
    )
    email = models.EmailField(
        blank = True,
        verbose_name = translate('Email')
    )

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = translate("Company settings")
        verbose_name_plural = translate("Company settings")

class SystemSettings(TimestampMixin, SingleRecordMixin):
    class CalendarPeriod(models.IntegerChoices):
        ONE_WEEK = 7, translate("1 week")
        TWO_WEEKS = 14, translate("2 weeks")
        ONE_MONTH = 30, translate("1 month")

    default_calendar_period = models.PositiveSmallIntegerField(
        choices = CalendarPeriod.choices,
        default = CalendarPeriod.TWO_WEEKS,
        verbose_name = translate("Default calendar period"),
    )
    show_weekends=models.BooleanField(
        default = False,
        verbose_name = translate("Show weekends"),
    )
    workday_start = models.TimeField(
        default = time(8, 0),
        verbose_name = translate("Workday start")
    )
    workday_end = models.TimeField(
        default = time(17,0),
        verbose_name = translate("Workday end"),
    )
    warning_days_before_due = models.PositiveSmallIntegerField(
        default = 14,
        verbose_name = translate("Warning days before due date"),
    )
    critical_days_before_due = models.PositiveSmallIntegerField(
        default = 3,
        verbose_name = translate("Critical days before due date"),
    )
    show_overdue_alerts = models.BooleanField(
        default = True,
        verbose_name = translate("Show overdue alerts"),
    )
    auto_create_next_inspection = models.BooleanField(
        default = True,
        verbose_name = translate("Automatically create next inspection"),
    )
    require_assigned_employee_before_start = models.BooleanField(
        default = True,
        verbose_name = translate("Require assigned employee before start"),
    )
    require_result_before_completion = models.BooleanField(
        default = True,
        verbose_name = translate("Require result before completion"),
    )

    def clean(self):
        super().clean()

        if self.workday_start >= self.workday_end:
            raise ValidationError(
                {"workday_end": translate("Workday end must be later than workday start.")}
            )

        if self.critical_days_before_due > self.warning_days_before_due:
            raise ValidationError(
                {"critical_days_before_due": translate("Critical days cannot be greater than warning days.")}
            )

    def __str__(self):
        return str(translate("System settings"))

    class Meta:
        verbose_name = translate("System settings")
        verbose_name_plural = translate("System settings")




