from django.db import transaction
from accounts.models import Person


@transaction.atomic
def register_user(form):
    user = form.save(commit=False)
    person = Person.objects.create(
        email=form.cleaned_data['email'],
        login_email_reserved=True
    )
    user.person = person
    user.save()
    return user
