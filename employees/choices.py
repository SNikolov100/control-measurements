from django.db import models
from django.utils.translation import gettext_lazy as translate

class EmployeeHistoryEventType(models.TextChoices):
    CREATED = 'created', translate('Created')
    UPDATED = 'updated', translate('Updated')
    SPECIALTY_ADDED = 'specialty_added', translate('Specialty added')
    SPECIALTY_REMOVED = 'specialty_removed', translate('Specialty removed')
    ACTIVATED = 'activated', translate('Activated')
    DEACTIVATED = 'deactivated', translate('Deactivated')


class EmployeeRequestStatus(models.TextChoices):
    PENDING = 'pending', translate('Pending')
    APPROVED = 'approved', translate('Approved')
    REJECTED = 'rejected', translate('Rejected')


class EmployeeRequestAction(models.TextChoices):
    LINK = 'link', translate('Link existing employee')
    CREATE = 'create', translate('Create new employee')
    REJECT = 'reject', translate('Reject request')

class PersonNameSource(models.TextChoices):
    EMPLOYEE = 'employee', translate('Keep name from existing employee record')
    ACCOUNT = 'account', translate('Keep name from registered account profile')

class PersonPhoneSource(models.TextChoices):
    EMPLOYEE = ('employee', translate('Keep phone from existing employee record'))
    ACCOUNT = ('account', translate('Keep phone from registered account profile'))