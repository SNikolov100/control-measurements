from django.http.response import HttpResponseRedirect
from core.view_mixins import PermissionAwareSuccessMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView
from .forms import EmployeeCreateForm, EmployeeEditForm, EmployeeActivityStatusForm
from .models import Employee
from core.view_mixins import PaginationMixin, SearchMixin, StatusFilterMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import EmployeeRequest
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from .forms import EmployeeRequestReviewForm
from .services import review_employee_request, reconsider_employee_request, create_employee_from_form, update_employee_from_form
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.db.models import Exists, OuterRef
from core.models import Specialty
from .choices import PersonNameSource, PersonPhoneSource

class EmployeeListView(SearchMixin, PaginationMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'

    search_fields = (
        'person__first_name__icontains',
        'person__middle_name__icontains',
        'person__last_name__icontains',
        'position__icontains',
        'person__phone__icontains',
        'person__email__icontains',
        'specialties__code__icontains',
        'specialties__name__icontains',
        'specialties__short_name__icontains',
    )
    search_distinct = True

    def get_queryset(self):
        queryset = super().get_queryset().select_related('person', 'user').prefetch_related('specialties', 'user__groups')
        active = self.request.GET.get('active', 'all')

        if active == 'active':
            queryset = queryset.filter(is_active=True)
        elif active == 'inactive':
            queryset = queryset.filter(is_active=False)

        specialty_ids = [int(value) for value in self.request.GET.getlist('specialty') if value.isdecimal()]
        if specialty_ids:
            queryset = queryset.filter(specialties__pk__in=specialty_ids).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialty_options'] = Specialty.objects.all()
        context['selected_specialty_ids'] = [int(value) for value in self.request.GET.getlist('specialty') if value.isdecimal()]
        active = self.request.GET.get('active', 'all')
        context['current_active_filter'] = active if active in ('all', 'active', 'inactive') else 'all'

        return context

class EmployeeCreateView(PermissionAwareSuccessMixin, CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    template_name = 'employees/employee_create.html'
    success_url = reverse_lazy('employees:list')

    def form_valid(self, form):
        employee = create_employee_from_form(form)
        self.object = employee
        return HttpResponseRedirect(self.get_success_url())

class EmployeeEditView(PermissionAwareSuccessMixin, UpdateView):
    model = Employee
    form_class = EmployeeEditForm
    template_name = 'employees/employee_edit.html'
    context_object_name = 'employee'
    success_url = reverse_lazy('employees:list')

    def form_valid(self, form):
        try:
            employee = update_employee_from_form(form)

        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)
            return self.form_invalid(form)

        except IntegrityError:
            form.add_error(None, 'The employee could not be updated. Please check the data.')
            return self.form_invalid(form)

        self.object = employee
        messages.success(self.request, 'Employee updated successfully.')

        return HttpResponseRedirect(self.get_success_url())

class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_queryset(self):
        queryset_result = super().get_queryset().prefetch_related('specialties', 'history')
        return queryset_result

class EmployeeActivityStatusView(PermissionAwareSuccessMixin, FormView):
    form_class = EmployeeActivityStatusForm
    template_name = 'employees/employee_activity_status.html'

    def dispatch(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee,pk=kwargs['pk'])
        return super().dispatch(request,*args,**kwargs,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee'] = self.employee
        return context

    def form_valid(self, form):
        description = form.cleaned_data['description']

        if self.employee.is_active:
            self.employee.deactivate(description)
        else:
            self.employee.activate(description)

        return super().form_valid(form)

    def get_preferred_success_url(self):
        return reverse('employees:list')

class PendingEmployeeRequestsView(UserPassesTestMixin,StatusFilterMixin, PaginationMixin, ListView):
    model = EmployeeRequest
    template_name = 'employees/pending_employee_requests.html'
    context_object_name = 'employee_requests'
    default_page_size = 10
    status_field = 'status'
    status_choices = EmployeeRequest.Status

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get_queryset(self):
        reconsidered_requests = EmployeeRequest.objects.filter(reconsidered_from_id=OuterRef('pk'))
        return (
            super().get_queryset()
            .select_related('user__person')
            .annotate(has_reconsideration=Exists(reconsidered_requests))
            .order_by('created_at')
        )


class EmployeeRequestReviewView(PermissionAwareSuccessMixin, UserPassesTestMixin, FormView):
    form_class = EmployeeRequestReviewForm
    template_name = 'employees/employee_request_review.html'
    success_url = reverse_lazy('employees:pending-requests')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_request'] = get_object_or_404(
            EmployeeRequest.objects.select_related('user', 'user__person',),
            pk=self.kwargs['pk'],
            status=EmployeeRequest.Status.PENDING,
        )
        return context

    def form_valid(self, form):
        try:
            review_employee_request(
                request_id=self.kwargs['pk'],
                reviewer=self.request.user,
                action=form.cleaned_data['action'],
                role=form.cleaned_data['role'],
                employee=form.cleaned_data['employee'],
                note=form.cleaned_data['review_note'],
                confirm_name_difference=form.cleaned_data['confirm_name_difference'],
                name_source=form.cleaned_data.get('name_source'),
                phone_source=form.cleaned_data.get('phone_source')
            )



        except ValidationError as error:
            confirmation_codes = {'name_mismatch', 'name_source_required', 'phone_source_required'}
            needs_confirmation = any(item.code in confirmation_codes for item in error.error_list)
            form.show_name_confirmation = False
            form.show_phone_confirmation = False

            if needs_confirmation:
                employee = form.cleaned_data.get('employee')
                employee_request = EmployeeRequest.objects.select_related('user__person').get(pk=self.kwargs['pk'])
                account_person = employee_request.user.person

                if employee and employee.person_id and account_person:
                    employee_person = employee.person
                    employee_name = employee_person.get_full_name()
                    account_name = account_person.get_full_name()
                    form.show_name_confirmation = ' '.join(employee_name.split()).casefold() != ' '.join(account_name.split()).casefold()
                    form.show_phone_confirmation = bool(employee_person.phone and account_person.phone and employee_person.phone.strip()!= account_person.phone.strip())

                    if form.show_name_confirmation:
                        form.fields['name_source'].required = True
                        form.fields['name_source'].choices = [
                            (PersonNameSource.EMPLOYEE, f'{PersonNameSource.EMPLOYEE.label}: {employee_name}'),
                            (PersonNameSource.ACCOUNT, f'{PersonNameSource.ACCOUNT.label}: {account_name}'),
                        ]

                    if form.show_phone_confirmation:
                        form.fields['phone_source'].required = True
                        form.fields['phone_source'].choices = [
                            (PersonPhoneSource.EMPLOYEE, f'{PersonPhoneSource.EMPLOYEE.label}: {employee_person.phone}'),
                            (PersonPhoneSource.ACCOUNT, f'{PersonPhoneSource.ACCOUNT.label}: {account_person.phone}'),
                        ]

            form.show_link_confirmation = form.show_name_confirmation or form.show_phone_confirmation
            for message in error.messages:
                form.add_error(None, message)

            return self.form_invalid(form)

        except IntegrityError:
            form.add_error(None, 'The request could not be processed. Please check the employee link and try again.',)
            return self.form_invalid(form)

        messages.success(self.request, 'Employee request processed successfully.',)
        return super().form_valid(form)


@login_required
@require_POST
def reconsider_employee_request_view(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied

    note = request.POST.get('note', '')
    rejected_url = reverse('employees:pending-requests') + '?status=rejected'
    try:
        reconsider_employee_request(request_id=pk, reviewer=request.user, note=note)

    except ValidationError as error:
        for message in error.messages:
            messages.error(request, message)
        return redirect(rejected_url)

    except IntegrityError:
        messages.error(request, 'The request could not be reconsidered. Please refresh the page and try again.')
        return redirect(rejected_url)

    messages.success(request, 'Employee request reopened successfully.')

    return redirect(reverse('employees:pending-requests') + '?status=pending')
