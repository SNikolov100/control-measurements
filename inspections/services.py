from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as translate
from django.utils import timezone

from inspections.models import Inspection


def start_inspection(inspection) ->Inspection:
    if inspection.pk is None:
        raise ValidationError(translate("The inspection must be saved before it can be started."))

    if not inspection.can_change_status_to(inspection.Status.IN_PROGRESS):
        raise ValidationError(
            {"status": translate("The inspection cannot be started from its current status.")}
        )

    another_activity_in_progress = (type(inspection).objects
                                    .filter(equipment_id=inspection.equipment_id, status=inspection.Status.IN_PROGRESS, )
                                    .exclude(pk=inspection.pk)
                                    .exists()
                                    )

    if another_activity_in_progress:
        raise ValidationError(
            {"status": translate("This equipment already has another activity in progress.")}
        )

    assigned_employees = inspection.assigned_employees.all()

    if not assigned_employees.exists():
        raise ValidationError(
            {"assigned_employees": translate("At least one employee must be assigned before the inspection can start.")}
        )

    inactive_employees = assigned_employees.filter(is_active=False)

    if inactive_employees.exists():
        raise ValidationError(
            {"assigned_employees": translate("Inactive employees cannot be assigned to an inspection.")}
        )

    required_specialty = inspection.equipment.equipment_type.specialty

    unqualified_employees = assigned_employees.exclude(specialties=required_specialty)

    if unqualified_employees.exists():
        raise ValidationError(
            {"assigned_employees": translate("All assigned employees must have the equipment specialty.")}
        )

    with transaction.atomic():
        inspection.status = inspection.Status.IN_PROGRESS
        inspection.actual_start = timezone.now()
        inspection.save(update_fields={"status", "actual_start", })

        if inspection.inspection_type == inspection.InspectionType.REPAIR:
            equipment_status = inspection.equipment.Status.UNDER_REPAIR
        else:
            equipment_status = inspection.equipment.Status.UNDER_INSPECTION

        inspection.equipment.change_status(
            equipment_status,
            reason=f"Inspection #{inspection.pk} started: {inspection.get_inspection_type_display()}."
        )

    return inspection


def complete_inspection(inspection, result="", result_notes="") ->Inspection:
    if not inspection.can_change_status_to(inspection.Status.COMPLETED):
        raise ValidationError(
            {"status": translate("The inspection cannot be completed from its current status.")}
        )

    result_required_types = {
        inspection.InspectionType.CALIBRATION,
        inspection.InspectionType.PERIODIC,
        inspection.InspectionType.EXTRAORDINARY,
        inspection.InspectionType.REINSPECTION,
    }

    if (inspection.inspection_type in result_required_types) and (result not in inspection.Result.values):
        raise ValidationError(
            {"result": translate("A valid result is required to complete this inspection.")}
        )

    if inspection.inspection_type == inspection.InspectionType.REPAIR and result:
        raise ValidationError(
            {"result": translate("Repair activities do not use an inspection result.")}
        )

    with transaction.atomic():
        inspection.status = inspection.Status.COMPLETED
        inspection.result = result
        inspection.result_notes = result_notes.strip()
        inspection.actual_end = timezone.now()

        inspection.save(update_fields={"status", "result", "result_notes", "actual_end"})

        if inspection.inspection_type == inspection.InspectionType.REPAIR:
            equipment_status = inspection.equipment.Status.WAITING_REINSPECTION

        elif result == inspection.Result.PASSED:
            equipment_status = inspection.equipment.Status.IN_SERVICE

        else:
            equipment_status = inspection.equipment.Status.UNDER_REPAIR

        inspection.equipment.change_status(
            equipment_status,
            reason=f"Inspection #{inspection.pk} completed: {inspection.get_inspection_type_display()}.",
            notes=inspection.result_notes,
        )

    return inspection


def cancel_inspection(inspection: Inspection, reason: str) -> Inspection:
    if not inspection.can_change_status_to(inspection.Status.CANCELLED):
        raise ValidationError(
            {"status": translate("The inspection cannot be cancelled from its current status.")}
        )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            {"cancellation_reason": translate("A cancellation reason is required.")}
        )

    was_in_progress = inspection.status == inspection.Status.IN_PROGRESS

    with transaction.atomic():
        inspection.status = inspection.Status.CANCELLED
        inspection.cancellation_reason = reason

        if was_in_progress and not inspection.actual_end:
            inspection.actual_end = timezone.now()

        inspection.save(update_fields={"status", "cancellation_reason", "actual_end",})

        if was_in_progress:
            if inspection.inspection_type == inspection.InspectionType.REPAIR:
                equipment_status = inspection.equipment.Status.TEMPORARILY_SUSPENDED

            elif inspection.inspection_type == inspection.InspectionType.REINSPECTION:
                equipment_status = inspection.equipment.Status.WAITING_REINSPECTION

            else:
                equipment_status = inspection.equipment.Status.IN_SERVICE

            inspection.equipment.change_status(
                equipment_status,
                reason=f"Inspection #{inspection.pk} cancelled: {inspection.get_inspection_type_display()}.",
                notes=reason,
            )

    return inspection
