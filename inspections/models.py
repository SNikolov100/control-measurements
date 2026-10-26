from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as translate
from core.model_mixins import TimestampMixin
from django.utils import timezone
from equipment.models import Equipment

class Inspection(TimestampMixin):
    class InspectionType(models.TextChoices):
        CALIBRATION = "calibration", translate("Calibration")
        PERIODIC = "periodic", translate("Periodic inspection")
        EXTRAORDINARY = "extraordinary", translate("Extraordinary inspection")
        REPAIR = "repair", translate("Repair")
        REINSPECTION = "reinspection", translate("Reinspection after repair")

    class Status(models.TextChoices):
        PENDING = "pending", translate("Pending")               #registered, but not start yet
        IN_PROGRESS = "in_progress", translate("In progress")
        COMPLETED = "completed", translate("Completed")
        CANCELLED = "cancelled", translate("Cancelled")

    class Result(models.TextChoices):
        PASSED = "passed", translate("Passed")
        FAILED = "failed", translate("Failed")

    result = models.CharField(
        max_length=10,
        choices=Result.choices,
        blank=True,
        verbose_name=translate("Result"),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=translate("Status"),
    )

    inspection_type = models.CharField(
        max_length=20,
        choices=InspectionType.choices,
        verbose_name=translate("Inspection type"),
    )
    equipment = models.ForeignKey(
        "equipment.Equipment",
        on_delete=models.PROTECT,
        related_name="inspections",
        verbose_name=translate("Equipment"),
    )
    previous_equipment_status = models.CharField(
        max_length=25,
        choices=Equipment.Status.choices,
        blank=True,
        editable=False,
        verbose_name=translate(
            "Previous equipment status"
        ),
    )
    customer_contact = models.ForeignKey(
        "customers.CustomerContact",
        on_delete=models.PROTECT,
        related_name="delivered_inspections",
        blank=True,
        null=True,
        verbose_name=translate("Customer contact"),
    )
    assigned_employees = models.ManyToManyField(
        "employees.Employee",
        related_name="inspections",
        blank=True,
        verbose_name=translate("Assigned employees"),
    )
    received_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=translate("Received at"),
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=translate("Due date"),
    )
    planned_start = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=translate("Planned start"),
    )
    actual_start = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=translate('Actual start'),
    )
    actual_end = models.DateTimeField(
        blank=True,
        null=True,
        editable=False,
        verbose_name=translate("Actual end"),
    )
    estimated_duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=translate("Estimated duration in minutes"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=translate("Notes"),
    )
    result_notes = models.TextField(
        blank=True,
        verbose_name=translate("Result notes"),
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name=translate("Cancellation reason"),
    )

    def can_change_status_to(self, new_status) -> bool:
        allowed_transitions: dict[str, set[str]] = {
            self.Status.PENDING: {self.Status.IN_PROGRESS, self.Status.CANCELLED,},
            self.Status.IN_PROGRESS: {self.Status.COMPLETED, self.Status.CANCELLED,},
            self.Status.COMPLETED: set(),
            self.Status.CANCELLED: set(),
        }
        return new_status in allowed_transitions.get(self.status, set())

    def clean(self):
        super().clean()
        errors = {}
        if self.equipment_id and self.customer_contact_id and (self.customer_contact.site_id != self.equipment.customer_site_id):
            errors["customer_contact"] = translate("The selected contact must belong to the equipment customer site.")

        if self.due_date and self.planned_start and (self.planned_start.date() > self.due_date):
            errors["planned_start"] = translate("Planned start cannot be after the due date.")

        if self.actual_start and self.actual_end and (self.actual_start > self.actual_end):
            errors["actual_end"] = translate("Actual end cannot be earlier than actual start.")

        result_required_types = {
            self.InspectionType.CALIBRATION,
            self.InspectionType.PERIODIC,
            self.InspectionType.EXTRAORDINARY,
            self.InspectionType.REINSPECTION,}

        if (self.status == self.Status.COMPLETED
            and self.inspection_type in result_required_types
            and not self.result):
            errors["result"] = translate("A completed inspection must have a result.")

        if self.inspection_type == self.InspectionType.REPAIR and self.result:
            errors["result"] = translate("Repair activities do not use an inspection result.")

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.get_inspection_type_display()} - {self.equipment}"

    class Meta:
        ordering = ("-received_at","-created_at")
        verbose_name = translate("Inspection")
        verbose_name_plural = translate("Inspections")




