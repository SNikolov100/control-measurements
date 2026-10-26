from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as translate
from django.utils import timezone
from inspections.models import Inspection

INSPECTION_TYPES = {
    Inspection.InspectionType.CALIBRATION,
    Inspection.InspectionType.PERIODIC,
    Inspection.InspectionType.EXTRAORDINARY,
}

def get_allowed_inspection_types(equipment):
    allowed_types_by_status = {
        equipment.Status.IN_SERVICE: (
            Inspection.InspectionType.CALIBRATION.value,
            Inspection.InspectionType.PERIODIC.value,
            Inspection.InspectionType.EXTRAORDINARY.value,
            Inspection.InspectionType.REPAIR.value,
        ),
        equipment.Status.UNDER_REPAIR: (
            Inspection.InspectionType.REPAIR.value,
        ),
        equipment.Status.WAITING_REINSPECTION: (
            Inspection.InspectionType.REINSPECTION.value,
        ),
    }

    return allowed_types_by_status.get(
        equipment.status,
        (),
    )




def register_pending_inspection(inspection: Inspection) -> Inspection:
    if inspection.pk is None:
        raise ValidationError(translate('The activity must be saved before the equipment status can be updated.'))

    if inspection.status != inspection.Status.PENDING:
        raise ValidationError(
            {'status': translate('A newly registered activity must have Pending status.')}
        )

    another_open_activity = (type(inspection).objects
        .filter(
            equipment_id=inspection.equipment_id,
            status__in=(inspection.Status.PENDING, inspection.Status.IN_PROGRESS,),
        )
        .exclude(pk=inspection.pk)
        .exists()
    )

    if another_open_activity:
        raise ValidationError(
            {'equipment': translate('This equipment already has another pending or in-progress activity.')}
        )

    allowed_inspection_types = get_allowed_inspection_types(inspection.equipment)

    if inspection.inspection_type not in allowed_inspection_types:
        if inspection.equipment.status == inspection.equipment.Status.UNDER_REPAIR:
            message = translate('Only a repair activity can be created while the equipment is under repair.')
        elif inspection.equipment.status == inspection.equipment.Status.WAITING_REINSPECTION:
            message = translate('Only a reinspection can be created while the equipment is waiting for reinspection.')
        else:
            message = translate('A new activity cannot be created while the equipment is in its current status.')

        raise ValidationError(
            {'inspection_type': message}
        )

    equipment = inspection.equipment
    previous_status = equipment.status
    inspection.previous_equipment_status = previous_status

    if inspection.inspection_type in INSPECTION_TYPES:
        new_equipment_status = equipment.Status.WAITING_INSPECTION

    elif inspection.inspection_type == inspection.InspectionType.REPAIR:
        new_equipment_status = equipment.Status.UNDER_REPAIR

    elif inspection.inspection_type == inspection.InspectionType.REINSPECTION:
        if equipment.status != equipment.Status.WAITING_REINSPECTION:
            raise ValidationError(
                {'inspection_type': translate('A reinspection after repair can be created only when the equipment is waiting for reinspection.')}
            )

        new_equipment_status = equipment.Status.WAITING_REINSPECTION

    else:
        raise ValidationError(
            {'inspection_type': translate('Unsupported activity type.')}
        )

    with transaction.atomic():
        inspection.save(update_fields=('previous_equipment_status',))
        equipment.change_status(
            new_equipment_status,
            reason=f'Inspection #{inspection.pk} registered: {inspection.get_inspection_type_display()}.')

    return inspection


def start_inspection(inspection) ->Inspection:
    if inspection.pk is None:
        raise ValidationError(translate('The inspection must be saved before it can be started.'))

    if not inspection.can_change_status_to(inspection.Status.IN_PROGRESS):
        raise ValidationError(
            {'status': translate('The inspection cannot be started from its current status.')}
        )

    another_activity_in_progress = (type(inspection).objects
                                    .filter(equipment_id=inspection.equipment_id, status=inspection.Status.IN_PROGRESS, )
                                    .exclude(pk=inspection.pk)
                                    .exists()
                                    )

    if another_activity_in_progress:
        raise ValidationError(
            {'status': translate('This equipment already has another activity in progress.')}
        )

    assigned_employees = inspection.assigned_employees.all()

    if not assigned_employees.exists():
        raise ValidationError(
            {'assigned_employees': translate('At least one employee must be assigned before the inspection can start.')}
        )

    inactive_employees = assigned_employees.filter(is_active=False)

    if inactive_employees.exists():
        raise ValidationError(
            {'assigned_employees': translate('Inactive employees cannot be assigned to an inspection.')}
        )

    required_specialty = inspection.equipment.equipment_type.specialty

    unqualified_employees = assigned_employees.exclude(specialties=required_specialty)

    if unqualified_employees.exists():
        raise ValidationError(
            {'assigned_employees': translate('All assigned employees must have the equipment specialty.')}
        )

    equipment = inspection.equipment

    if inspection.inspection_type == inspection.InspectionType.REINSPECTION:
        allowed_equipment_statuses = {equipment.Status.WAITING_REINSPECTION}

    elif inspection.inspection_type == inspection.InspectionType.REPAIR:
        allowed_equipment_statuses = {equipment.Status.UNDER_REPAIR}

    else:
        allowed_equipment_statuses = {equipment.Status.WAITING_INSPECTION}

    if equipment.status not in allowed_equipment_statuses:
        raise ValidationError({
                'status': translate('The equipment is not in the expected status for starting this activity.')
            }
        )

    with transaction.atomic():
        inspection.status = inspection.Status.IN_PROGRESS
        inspection.actual_start = timezone.now()
        inspection.save(update_fields={'status', 'actual_start', })

        if inspection.inspection_type == inspection.InspectionType.REPAIR:
            equipment_status = inspection.equipment.Status.UNDER_REPAIR
        else:
            equipment_status = inspection.equipment.Status.UNDER_INSPECTION

        inspection.equipment.change_status(
            equipment_status,
            reason=f"Inspection #{inspection.pk} started: {inspection.get_inspection_type_display()}."
        )

    return inspection


def complete_inspection(inspection, result='', result_notes='') -> Inspection:
    if not inspection.can_change_status_to(inspection.Status.COMPLETED):
        raise ValidationError(
            {'status': translate('The activity cannot be completed from its current status.')}
        )

    if result not in inspection.Result.values:
        raise ValidationError(
            {'result': translate('A valid result is required to complete this activity.')}
        )

    result_notes = result_notes.strip()

    if inspection.inspection_type == inspection.InspectionType.REPAIR.value and not result_notes:
        raise ValidationError(
            {'result_notes': translate('Describe the repair work performed and the final repair outcome.')}
        )

    if result == inspection.Result.FAILED.value and not result_notes:
        raise ValidationError(
            {'result_notes': translate('Describe why the activity was unsuccessful.')}
        )

    if inspection.inspection_type == inspection.InspectionType.REPAIR.value:
        if result == inspection.Result.PASSED.value:
            equipment_status = inspection.equipment.Status.WAITING_REINSPECTION
        else:
            equipment_status = inspection.equipment.Status.UNDER_REPAIR

    elif result == inspection.Result.PASSED.value:
        equipment_status = inspection.equipment.Status.IN_SERVICE

    else:
        equipment_status = inspection.equipment.Status.UNDER_REPAIR

    with transaction.atomic():
        inspection.status = inspection.Status.COMPLETED
        inspection.result = result
        inspection.result_notes = result_notes
        inspection.actual_end = timezone.now()
        inspection.save(update_fields=('status', 'result', 'result_notes', 'actual_end'))

        inspection.equipment.change_status(
            equipment_status,
            reason=f'Inspection #{inspection.pk} completed: {inspection.get_inspection_type_display()}.',
            notes=inspection.result_notes,
        )

    return inspection


def cancel_inspection(inspection: Inspection,reason: str) -> Inspection:
    if not inspection.can_change_status_to(inspection.Status.CANCELLED):
        raise ValidationError({
                'status': translate('The inspection cannot be cancelled from its current status.')
        })

    reason = reason.strip()

    if not reason:
        raise ValidationError({
                'cancellation_reason': translate('A cancellation reason is required.')
        })

    was_in_progress = inspection.status == inspection.Status.IN_PROGRESS
    equipment = inspection.equipment
    restored_status = inspection.previous_equipment_status or equipment.Status.IN_SERVICE

    with transaction.atomic():
        inspection.status = inspection.Status.CANCELLED
        inspection.cancellation_reason = reason
        update_fields = {'status', 'cancellation_reason'}

        if was_in_progress and not inspection.actual_end:
            inspection.actual_end = timezone.now()
            update_fields.add('actual_end')

        inspection.save(update_fields=update_fields)
        equipment.change_status(restored_status,
            reason=f'Inspection #{inspection.pk} cancelled: {inspection.get_inspection_type_display()}.',
            notes=reason,
        )

    return inspection

