from django.db import models
from django.utils.translation import gettext_lazy as translate

class UserRole(models.TextChoices):
    EMPLOYEE = 'Employee', translate('Employee')
    OPERATOR = 'Operator', translate('Operator')

GROUP_EMPLOYEE = UserRole.EMPLOYEE.value
GROUP_OPERATOR = UserRole.OPERATOR.value