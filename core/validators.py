from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as translate
from pathlib import Path
from django.core.exceptions import ValidationError

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


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024

def validate_uploaded_image(image):
    file_extension = Path(image.name).suffix.lower()

    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            translate('Upload a JPEG, PNG, or WebP image.')
        )

    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            translate('The image must not be larger than 5 MB.')
        )