from django.core.exceptions import ValidationError
from django.db import models
from .model_mixins import TimestampMixin, SingleRecordMixin, CompanyMixin, TextNormalizationMixin
from django.utils.translation import gettext_lazy as translate
from .validators import hex_color_validator
from datetime import time

class Specialty(TextNormalizationMixin, TimestampMixin):
    strip_fields = ('code', 'name', 'short_name', 'description', 'color',)

    uppercase_fields = ('code', 'color',)
    code = models.CharField(
        max_length = 20,
        unique=True,
        verbose_name = translate('Code'),
        error_messages={
            "blank": translate("Enter a code for the specialty."),
            "unique": translate("A specialty with this code already exists."),
            "max_length": translate("The specialty code cannot contain more than 20 characters."),
        },
    )
    name = models.CharField(
        max_length = 150,
        unique = True,
        verbose_name = translate('Name'),
        error_messages={
            "blank": translate("Enter the specialty name."),
            "unique": translate("A specialty with this name already exists."),
            "max_length": translate("The specialty name cannot contain more than 150 characters."),
        },
    )
    short_name = models.CharField(
        max_length = 50,
        blank = True,
        verbose_name = translate('Short name'),
        error_messages={
            "max_length": translate("The short name cannot contain more than 50 characters."),
        },
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
        error_messages={
            "blank": translate("Enter a color in the format #RRGGBB."),
            "max_length": translate("Enter a valid HEX color in the format #RRGGBB."),
        },
    )
    sort_order = models.PositiveIntegerField(
        default = 0,
        verbose_name = translate("Sort order"),
    )
    is_active = models.BooleanField(
        default = True,
        verbose_name = translate("Active"),
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = translate("Specialty")
        verbose_name_plural = translate("Specialties")

class CompanySettings(CompanyMixin, TimestampMixin, SingleRecordMixin):
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




