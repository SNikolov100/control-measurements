def get_access_state(user):

    if not user.is_authenticated:
        return 'anonymous'

    if user.is_superuser:
        return 'ready'

    if user.registration_status == user.RegistrationStatus.REJECTED:
        return 'rejected'

    if user.registration_status != user.RegistrationStatus.APPROVED:
        return 'pending'

    if not hasattr(user, "profile"):
        return 'profile_required'

    if not hasattr(user, "employee"):
        return 'employee_pending'

    return 'ready'