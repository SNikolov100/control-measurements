from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView
from .forms import EmployeeCreateForm, EmployeeEditForm, EmployeeActivityStatusForm
from .models import Employee
from core.view_mixins import PaginationMixin, SearchMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import EmployeeRequest
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .forms import EmployeeRequestReviewForm
from .services import review_employee_request

class EmployeeListView(SearchMixin, PaginationMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'

    search_fields = (
        'full_name__icontains',
        'position__icontains',
        'phone__icontains',
        'email__icontains',
        'specialties__code__icontains',
        'specialties__name__icontains',
        'specialties__short_name__icontains',
    )
    search_distinct = True

    def get_queryset(self):
        queryset_result = super().get_queryset().prefetch_related("specialties")
        return queryset_result

class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeCreateForm
    template_name = 'employees/employee_create.html'
    success_url = reverse_lazy('employees:list')

class EmployeeEditView(UpdateView):
    model = Employee
    form_class = EmployeeEditForm
    template_name = 'employees/employee_edit.html'
    context_object_name = 'employee'
    success_url = reverse_lazy('employees:list')

class EmployeeDetailView(DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_queryset(self):
        queryset_result = super().get_queryset().prefetch_related('specialties', 'history')
        return queryset_result

class EmployeeActivityStatusView(FormView):
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

    def get_success_url(self):
        return reverse('employees:list')

class PendingEmployeeRequestsView(UserPassesTestMixin, PaginationMixin, ListView):
    model = EmployeeRequest
    template_name = 'employees/pending_employee_requests.html'
    context_object_name = 'employee_requests'
    default_page_size = 10

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def get_queryset(self):
        return (EmployeeRequest.objects
            .filter(status=EmployeeRequest.Status.PENDING)
            .select_related('user', 'user__profile')
            .order_by('created_at')
        )

class EmployeeRequestReviewView(UserPassesTestMixin, FormView):
    form_class = EmployeeRequestReviewForm
    template_name = 'employees/employee_request_review.html'
    success_url = reverse_lazy('employees:pending-requests')

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_request'] = get_object_or_404(
            EmployeeRequest.objects.select_related('user', 'user__profile',),
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
            )

        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)
            return self.form_invalid(form)

        except IntegrityError:
            form.add_error(None, 'The request could not be processed. Please check the employee link and try again.',)
            return self.form_invalid(form)

        messages.success(self.request, 'Employee request processed successfully.',)
        return super().form_valid(form)

