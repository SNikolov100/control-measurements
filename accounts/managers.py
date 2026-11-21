from django.contrib.auth.models import UserManager
from django.db import transaction
class AppUserManager(UserManager):

    @transaction.atomic
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        from accounts.models import Person

        if not email or not email.strip():
            raise ValueError('Superuser must have an email address.')
        email = email.strip().lower()
        user = super().create_superuser(username, email, password, **extra_fields)
        person = Person.objects.create(email=email, login_email_reserved=True)
        user.person = person
        user.save(update_fields=['person'])
        return user