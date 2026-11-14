from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as translate


def validate_username_no_at(value):
    if "@" in value:
        raise ValidationError(
            translate("Username cannot contain '@'."),
            code='invalid_username',
        )