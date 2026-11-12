from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView, ListView
from .forms import AppUserRegistrationForm
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as translate

AppUser = get_user_model()
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


class PendingRegistrationsView(UserPassesTestMixin, ListView):
    model = AppUser
    template_name = 'accounts/pending_registrations.html'
    context_object_name = 'pending_users'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get_queryset(self):
        return AppUser.objects.filter(
            registration_status=AppUser.RegistrationStatus.PENDING,
            is_superuser=False,
        ).order_by('date_joined')

class AppUserLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

@login_required
@require_POST
def registration_decision(request, pk, action):

    if not request.user.is_superuser:
        raise PermissionDenied

    statuses = {
        "approve": AppUser.RegistrationStatus.APPROVED,
        "reject": AppUser.RegistrationStatus.REJECTED,
    }
    status = statuses.get(action)

    if status is None:
        raise Http404

    updated = AppUser.objects.filter(
        pk=pk,
        registration_status=AppUser.RegistrationStatus.PENDING,
        is_superuser=False,
    ).update(registration_status=status)

    if updated:
        messages.success(request, translate(f"Registration successfully {status}."))
    else:
        messages.warning(request, translate("Registration not found or already processed."))

    return redirect("accounts:pending_registrations")