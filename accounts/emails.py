from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from .tokens import make_email_verification_token
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone


def send_verification_email(user, request):
    token = make_email_verification_token(user)
    path = reverse('accounts:verify_email', kwargs={'token': token})
    verification_url = request.build_absolute_uri(path)
    now = timezone.now()
    time_delay = now - timedelta(minutes=1)
    AppUser = get_user_model()

    eligible_users = AppUser.objects.filter(
        pk=user.pk,
        email=user.email,
        is_active=True,
        registration_status=AppUser.RegistrationStatus.APPROVED,
        email_verified=False,
    )

    reserved = eligible_users.filter(
        Q(email_verification_sent_at__isnull=True)
        |
        Q(email_verification_sent_at__lte=time_delay)
    ).update(email_verification_sent_at=now)

    if not reserved:
        return False

    try:
        sent = send_mail(
            subject='Confirm your email — Control Measurements',
            message=(
                'Your registration has been approved.\n\n'
                'Please open the link below to confirm your email address:\n\n'
                f'{verification_url}\n\n'
                'This link is valid for 24 hours.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception:
        AppUser.objects.filter(
            pk=user.pk,
            email_verification_sent_at=now,
        ).update(email_verification_sent_at=None)
        raise

    if sent != 1:
        AppUser.objects.filter(
            pk=user.pk,
            email_verification_sent_at=now,
        ).update(email_verification_sent_at=None)
        return False

    return True