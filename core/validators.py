from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as translate


hex_color_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message=translate('Enter a valid HEX color in the format #RRGGBB.'),
    code='invalid_hex_color',
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9][0-9\s().-]{6,24}$",
    message=translate(
        "Enter a valid phone number containing digits, spaces, "
        "parentheses, dots or hyphens."
    ),
    code="invalid_phone_number",
)