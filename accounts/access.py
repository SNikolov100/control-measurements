from employees.models import EmployeeRequest

def get_access_state(user):

    if not user.is_authenticated:
        return 'anonymous'

    if user.is_superuser:
        return 'ready'

    if user.registration_status == user.RegistrationStatus.REJECTED:
        return 'rejected'

    if user.registration_status != user.RegistrationStatus.APPROVED:
        return 'pending'

    if not user.email_verified:
        return 'email_verification_required'

    if not hasattr(user, 'profile'):
        return 'profile_required'

    if not hasattr(user, 'employee'):
        latest_status = (
            EmployeeRequest.objects
            .filter(user_id=user.pk)
            .order_by('-created_at', '-pk')
            .values_list('status', flat=True)
            .first()
        )

        if latest_status == EmployeeRequest.Status.REJECTED:
            return 'employee_rejected'

        return 'employee_pending'

    return 'ready'