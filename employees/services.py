from accounts.models import AppUser, Profile
from .models import Employee, EmployeeRequest
from django.utils.translation import gettext_lazy as translate
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from .models import EmployeeHistory
from .choices import EmployeeRequestAction
from functools import partial
from .emails import send_employee_request_result_email

def ensure_employee_request(user):
    if user.registration_status != AppUser.RegistrationStatus.APPROVED:
        raise ValueError(translate('User account is not approved.'))

    if not Profile.objects.filter(user=user).exists():
        raise ValueError(translate('User profile does not exist.'))

    if Employee.objects.filter(user=user).exists():
        return None, False

    employee_request, created = EmployeeRequest.objects.get_or_create(
        user=user,
        status=EmployeeRequest.Status.PENDING,
    )

    return employee_request, created


@transaction.atomic
def review_employee_request(*,
    request_id: int,
    reviewer,
    action: str,
    role: Group | None = None,
    employee=None,
    note: str = '',
    confirm_name_difference: bool = False):
    if not reviewer.is_authenticated or not reviewer.is_superuser:
        raise PermissionDenied

    if action not in EmployeeRequestAction.values:
        raise ValidationError(translate('Invalid action.'))

    note = note.strip()
    if action == EmployeeRequestAction.REJECT and not note:
        raise ValidationError(translate('Rejection reason is required.'))

    group = None
    if action != EmployeeRequestAction.REJECT:
        if not isinstance(role, Group) or role.pk is None:
            raise ValidationError(translate('Select a valid permission group.'))
        group = Group.objects.filter(pk=role.pk).first()
        if group is None:
            raise ValidationError(translate('The selected group no longer exists.'))

    if action == EmployeeRequestAction.LINK and employee is None:
        raise ValidationError(translate('Select an employee.'))

    new_status = EmployeeRequest.Status.REJECTED if action == EmployeeRequestAction.REJECT else EmployeeRequest.Status.APPROVED
    updated = (EmployeeRequest.objects
        .filter(pk=request_id, status=EmployeeRequest.Status.PENDING)
        .update(status=new_status, reviewed_by=reviewer, reviewed_at=timezone.now(), review_note=note,)
    )
    if updated != 1:
        raise ValidationError(translate('This request has already been processed.'))

    employee_request = EmployeeRequest.objects.select_related('user', 'user__profile').get(pk=request_id)
    if action == EmployeeRequestAction.REJECT:
        transaction.on_commit(
            partial(send_employee_request_result_email, employee_request.user.email, employee_request.status),
            robust=True,
        )
        return employee_request

    user = employee_request.user
    if user.registration_status != user.RegistrationStatus.APPROVED:
        raise ValidationError(translate('User account is not approved.'))

    if user.is_superuser:
        raise ValidationError(translate('Cannot link a superuser account.'))

    if not hasattr(user, 'profile'):
        raise ValidationError(translate('User profile is missing.'))

    if Employee.objects.filter(user=user).exists():
        raise ValidationError(translate('This user already has an employee record.'))

    history_details = []
    if action == EmployeeRequestAction.CREATE:
        employee = Employee.objects.create(user=user, full_name=user.profile.get_full_name(), phone=user.profile.phone, email=user.email)
        event_type = EmployeeHistory.EventType.CREATED

    else:
        employee = Employee.objects.filter(pk=employee.pk, user__isnull=True, is_active=True).first()

        if employee is None:
            raise ValidationError(translate('The selected employee is no longer available.'))

        account_email = user.email.strip().lower()
        employee_email = employee.email.strip().lower()
        if employee_email and employee_email != account_email:
            raise ValidationError(
                translate(
                    "The selected employee's email (%(employee_email)s) "
                    "differs from the account email (%(account_email)s). "
                    "Select the correct employee or correct the employee record and try again."
                ),
                params={'employee_email': employee.email, 'account_email': user.email},
            )

        profile_name = user.profile.get_full_name()
        normalized_employee_name = (' '.join(employee.full_name.split()).casefold())
        normalized_profile_name = ' '.join(profile_name.split()).casefold()
        names_differ = normalized_employee_name != normalized_profile_name
        if names_differ and not confirm_name_difference:
            raise ValidationError(
                translate(
                    "The employee name (%(employee_name)s) differs "
                    "from the personal profile name (%(profile_name)s). "
                    "Check the selected employee. If this is the same "
                    "person, select the name confirmation checkbox and submit again."
                ),
                params={'employee_name': employee.full_name, 'profile_name': profile_name},
                code='name_mismatch',
            )

        updates = {'user': user}
        if not employee_email:
            updates['email'] = account_email
            history_details.append('Empty employee email filled from the account.')

        if names_differ:
            history_details.append(f'Name difference confirmed: employee "{employee.full_name}", profile "{profile_name}". Employee name preserved.')

        updated_employee = (Employee.objects
            .filter(
                pk=employee.pk,
                user__isnull=True,
                is_active=True,
                email=employee.email,
                full_name=employee.full_name,
            )
            .update(**updates)
        )
        if updated_employee != 1:
            raise ValidationError(translate('The employee record changed during review. Reload the page and check the details again.'))

        employee.refresh_from_db()
        event_type = EmployeeHistory.EventType.UPDATED

    history_description = f'Account linked to {user.username} by {reviewer.username} via request #{request_id}.'
    if history_details:
        history_description += ' ' + ' '.join(history_details)

    EmployeeHistory.objects.create(employee=employee, event_type=event_type, description=history_description)
    user.groups.set([group])
    EmployeeRequest.objects.filter(pk=request_id,).update(employee=employee)
    employee_request.employee = employee
    transaction.on_commit(
        partial(send_employee_request_result_email, employee_request.user.email, employee_request.status),
        robust=True,
    )

    return employee_request


@transaction.atomic
def reconsider_employee_request(*, request_id: int, reviewer, note: str):
    if not reviewer.is_authenticated or not reviewer.is_superuser:
        raise PermissionDenied

    note = note.strip()
    if not note:
        raise ValidationError(translate('Reconsideration reason is required.'))

    old_request = (
        EmployeeRequest.objects
        .select_for_update()
        .select_related('user')
        .filter(pk=request_id, status=EmployeeRequest.Status.REJECTED)
        .first()
    )
    if old_request is None:
        raise ValidationError(translate('The request is not rejected or does not exist.'))

    if EmployeeRequest.objects.filter(reconsidered_from=old_request).exists():
        raise ValidationError(translate('This request has already been reconsidered.'))

    user = old_request.user
    if not user.is_active or user.is_superuser or user.registration_status != user.RegistrationStatus.APPROVED or not user.email_verified:
        raise ValidationError(translate('The user account is not eligible for reconsideration.'))

    if not Profile.objects.filter(user=user).exists():
        raise ValidationError(translate('The user profile does not exist.'))

    if Employee.objects.filter(user=user).exists():
        raise ValidationError(translate('This user already has an employee record.'))

    if EmployeeRequest.objects.filter(user=user, status=EmployeeRequest.Status.PENDING).exists():
        raise ValidationError(translate('The user already has a pending request.'))

    new_request = EmployeeRequest.objects.create(
        user=user,
        status=EmployeeRequest.Status.PENDING,
        reconsidered_from=old_request,
        reconsidered_by=reviewer,
        reconsideration_note=note,
    )

    return new_request
