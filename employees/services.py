from accounts.models import AppUser, Profile
from .models import Employee, EmployeeRequest
from django.utils.translation import gettext_lazy as translate
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from accounts.roles import GROUP_EMPLOYEE, GROUP_OPERATOR
from .models import EmployeeHistory
from .choices import EmployeeRequestAction
from accounts.roles import UserRole

def ensure_employee_request(user):
    if user.registration_status != AppUser.RegistrationStatus.APPROVED:
        raise ValueError(translate("User account is not approved."))

    if not Profile.objects.filter(user=user).exists():
        raise ValueError(translate("User profile does not exist."))

    if Employee.objects.filter(user=user).exists():
        return None, False

    employee_request, created = EmployeeRequest.objects.get_or_create(
        user=user,
        status=EmployeeRequest.Status.PENDING,
    )

    return employee_request, created


@transaction.atomic
def review_employee_request(*, request_id: int, reviewer, action: str, role: str|None=None, employee=None, note: str = ''):
    if not reviewer.is_authenticated or not reviewer.is_superuser:
        raise PermissionDenied

    if action not in EmployeeRequestAction.values:
        raise ValidationError(translate('Invalid action.'))

    note = note.strip()
    if action == EmployeeRequestAction.REJECT and not note:
        raise ValidationError(translate('Rejection reason is required.'))

    if action != EmployeeRequestAction.REJECT and role not in UserRole.values:
        raise ValidationError(translate('Invalid user role.'))

    if action == EmployeeRequestAction.LINK and employee is None:
        raise ValidationError(translate('Select an employee.'))

    new_status = EmployeeRequest.Status.REJECTED if action == EmployeeRequestAction.REJECT else EmployeeRequest.Status.APPROVED
    updated = (EmployeeRequest.objects
        .filter(pk=request_id,  status=EmployeeRequest.Status.PENDING)
        .update(status=new_status, reviewed_by=reviewer, reviewed_at=timezone.now(), review_note=note,)
    )

    if updated != 1:
        raise ValidationError(translate('This request has already been processed.'))

    employee_request = (EmployeeRequest.objects
        .select_related('user', 'user__profile')
        .get(pk=request_id)
    )

    if action == EmployeeRequestAction.REJECT:
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

    if action == EmployeeRequestAction.CREATE:
        employee = Employee.objects.create(
            user=user,
            full_name=user.profile.get_full_name(),
            phone=user.profile.phone,
            email=user.email,
        )
        event_type = EmployeeHistory.EventType.CREATED

    else:
        updated_employee = Employee.objects.filter(
            pk=employee.pk,
            user__isnull=True,
            is_active=True,
        ).update(user=user)

        if updated_employee != 1:
            raise ValidationError(translate('The selected employee is no longer available.'))

        employee = Employee.objects.get(pk=employee.pk)
        event_type = EmployeeHistory.EventType.UPDATED

    EmployeeHistory.objects.create(
        employee=employee,
        event_type=event_type,
        description=f'Account linked to {user.username} by {reviewer.username} via request #{request_id}.',
    )
    group = Group.objects.get(name=role)
    user.groups.set([group])
    EmployeeRequest.objects.filter(pk=request_id,).update(employee=employee)
    employee_request.employee = employee

    return employee_request
