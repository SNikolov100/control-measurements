from django.db import transaction
from .access import get_access_state
from .models import Profile, RegistrationStatusHistory
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic import FormView, TemplateView, ListView, CreateView
from .forms import AppUserRegistrationForm, ProfileForm
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as translate
from .forms import AppUserLoginForm
from employees.services import ensure_employee_request
from django.core.signing import BadSignature, SignatureExpired
from .tokens import read_email_verification_token
from functools import partial
from .emails import send_verification_email, send_registration_rejected_email
import logging
from smtplib import SMTPException
from core.view_mixins import StatusFilterMixin, PaginationMixin

AppUser = get_user_model()
logger = logging.getLogger(__name__)
class AppUserRegistrationView(FormView):
    form_class = AppUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:registration_pending')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,translate('Your registration has been submitted successfully.'))
        return super().form_valid(form)

class RegistrationPendingView(TemplateView):
    template_name = 'accounts/registration_pending.html'


class PendingRegistrationsView(UserPassesTestMixin, StatusFilterMixin, PaginationMixin, ListView):
    model = AppUser
    template_name = 'accounts/pending_registrations.html'
    context_object_name = 'registrations'
    paginate_by = 20
    status_field = 'registration_status'
    status_choices = AppUser.RegistrationStatus

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=False).order_by('date_joined')


@login_required
@require_POST
def registration_decision(request, pk, action):
    if not request.user.is_superuser:
        raise PermissionDenied

    statuses = {
        'approve': AppUser.RegistrationStatus.APPROVED,
        'reject': AppUser.RegistrationStatus.REJECTED,
        'reconsider': AppUser.RegistrationStatus.PENDING,
    }
    status = statuses.get(action)
    if status is None:
        raise Http404

    if action == 'reconsider':
        expected_status = AppUser.RegistrationStatus.REJECTED
    else:
        expected_status = AppUser.RegistrationStatus.PENDING

    note = request.POST.get('note', '').strip()
    if action == 'reconsider' and not note:
        messages.error(request, 'Please provide a reason for reconsideration.')
        return redirect('accounts:pending_registrations')

    with (transaction.atomic()):
        updated = AppUser.objects.filter(
            pk=pk,
            registration_status=expected_status,
            is_superuser=False,
        ).update(registration_status=status)
        if updated:
            user = AppUser.objects.get(pk=pk)
            RegistrationStatusHistory.objects.create(
                user=user,
                changed_by=request.user,
                action=action,
                previous_status=expected_status,
                new_status=status,
                note=note,
            )

            if status == AppUser.RegistrationStatus.APPROVED:
                transaction.on_commit(
                    partial(send_verification_email, user, request),
                    robust=True,
                )
            elif status == AppUser.RegistrationStatus.REJECTED:
                transaction.on_commit(
                    partial(send_registration_rejected_email, user),
                    robust=True,
                )

    if updated:
        messages.success(request, translate(f'Registration successfully {status}.'))
    else:
        messages.warning(request, translate('Registration not found or already processed.'))

    return redirect('accounts:pending_registrations')

class ProfileCreateView(UserPassesTestMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('core:home')

    def test_func(self):
        return get_access_state(self.request.user) == 'profile_required'

    def form_valid(self, form):
        form.instance.user = self.request.user
        with transaction.atomic():
            response = super().form_valid(form)
            ensure_employee_request(self.request.user)

        messages.success(self.request, translate('Your profile was saved successfully.'))
        return response

class AppUserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AppUserLoginForm
    redirect_authenticated_user = True


@require_http_methods(["GET", "POST"])
def verify_email(request, token):
    template_name = 'accounts/verify_email.html'
    try:
        data = read_email_verification_token(token)
    except SignatureExpired:
        return render(request, template_name, {'error': translate('This confirmation link has expired.')}, status=400)
    except BadSignature:
        return render(request, template_name, {'error': translate('This confirmation link is invalid.')}, status=400)

    eligible_users = AppUser.objects.filter(
        pk=data['user_id'],
        email=data['email'],
        is_active=True,
        registration_status=AppUser.RegistrationStatus.APPROVED,
    )
    user = eligible_users.first()
    if user is None:
        return render(request, template_name, {'error': translate('This link cannot be used to confirm an email address.')}, status=400)

    if user.email_verified:
        return render(request, template_name, {'confirmed': True})

    if request.method == 'POST':
        updated = eligible_users.filter(email_verified=False).update(email_verified=True)

        if not updated:
            return render(request, template_name, {'error': translate('The account has changed. Please open the link again.')}, status=400)

        return redirect('accounts:verify_email', token=token)

    return render(request, template_name)


@login_required
@require_POST
def resend_verification_email(request):
    if get_access_state(request.user) != 'email_verification_required':
        return redirect('core:home')
    try:
        sent = send_verification_email(request.user, request)
    except (SMTPException, OSError):
        logger.exception('Could not send email verification message.')
        messages.error(request, translate('The email could not be sent. Please try again later.'))
    else:
        if sent:
            messages.success(request, translate('A new confirmation email has been sent.'))
        else:
            messages.warning(request, translate('No new email was sent. Please wait at least one minute between requests and refresh the page.'))

    return redirect('core:home')