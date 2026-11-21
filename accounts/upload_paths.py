from pathlib import Path
from uuid import uuid4


def person_photo_upload_path(instance, filename):
    file_extension = Path(filename).suffix.lower()
    return f'persons/{uuid4().hex}{file_extension}'

def profile_photo_upload_path(instance, filename):
    file_extension = Path(filename).suffix.lower()
    return f'profile/{uuid4().hex}{file_extension}'
