from core.view_mixins import PermissionAwareSuccessMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from equipment.models import Equipment
from .forms import InspectionCreateForm, InspectionAssignmentForm, InspectionStartForm, InspectionCompleteForm, InspectionCancelForm, InspectionInterruptForm
from .models import Inspection, InspectionHistory
from django.urls import reverse, reverse_lazy
from .services import (
    cancel_inspection, complete_inspection, get_allowed_inspection_types, register_pending_inspection,
    start_inspection, interrupt_inspection,  record_inspection_event, get_assigned_employees_snapshot)
from .view_mixins import InspectionActionMixin
from core.view_mixins import PaginationMixin, SearchMixin, StatusFilterMixin
from django.utils.translation import gettext_lazy as translate
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from .access import filter_inspections_for_user

class InspectionListView(PermissionRequiredMixin, StatusFilterMixin, SearchMixin, PaginationMixin, ListView):
    permission_required = 'inspections.view_inspection'
    raise_exception = True
    model = Inspection
    template_name = 'inspections/inspection_list.html'
    context_object_name = 'inspections'
    status_choices = Inspection.Status
    overdue_filter = 'overdue'
    search_fields = (
        'equipment__serial_number__icontains',
        'equipment__inventory_number__icontains',
        'equipment__model_name__icontains',
        'equipment__equipment_type__name__icontains',
        'equipment__equipment_type__short_name__icontains',
        'equipment__equipment_type__specialty__code__icontains',
        'equipment__equipment_type__specialty__name__icontains',
        'equipment__equipment_type__specialty__short_name__icontains',
        'equipment__customer_site__customer__company_name__icontains',
        'equipment__customer_site__customer__short_name__icontains',
        'equipment__customer_site__name__icontains',
        'equipment__customer_site__short_name__icontains',
        'assigned_employees__person__first_name__icontains',
        'assigned_employees__person__middle_name__icontains',
        'assigned_employees__person__last_name__icontains',
        'customer_contact__full_name__icontains',
        'notes__icontains',
        'result_notes__icontains',
        'cancellation_reason__icontains',
    )
    search_distinct = True

    def get_status_filters(self):
        filters = super().get_status_filters()
        filters.append({
                'value': self.overdue_filter,
                'label': translate('Overdue'),
        })
        return filters

    def filter_by_status(self, queryset, status_filter):
        if status_filter == self.overdue_filter:
            return queryset.filter(
                status__in=(Inspection.Status.PENDING, Inspection.Status.IN_PROGRESS, Inspection.Status.INTERRUPTED),
                due_date__lt=timezone.localdate(),
            )
        return super().filter_by_status(queryset,status_filter)

    def get_queryset(self):
        queryset_result = (super().get_queryset()
            .select_related(
                'customer_contact',
                'equipment',
                'equipment__equipment_type',
                'equipment__equipment_type__specialty',
                'equipment__customer_site',
                'equipment__customer_site__customer',
            )
            .prefetch_related('assigned_employees')
        )
        return filter_inspections_for_user(queryset_result, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_status_filter = self.get_status_filter()
        status_filters = (
            {'value': '', 'label': 'All'},
            {'value': Inspection.Status.PENDING.value, 'label': Inspection.Status.PENDING.label},
            {'value': Inspection.Status.IN_PROGRESS.value, 'label': Inspection.Status.IN_PROGRESS.label},
            {'value': Inspection.Status.INTERRUPTED.value, 'label': Inspection.Status.INTERRUPTED.label},
            {'value': Inspection.Status.COMPLETED.value, 'label': Inspection.Status.COMPLETED.label},
            {'value': Inspection.Status.CANCELLED.value, 'label': Inspection.Status.CANCELLED.label},
            {'value': self.overdue_filter, 'label': translate('Overdue')},
        )
        current_status_label = ''
        for status_filter in status_filters:
            if status_filter['value'] == current_status_filter:
                current_status_label = status_filter['label']
                break

        context['current_status_filter'] = current_status_filter
        context['current_status_label'] = current_status_label
        context['status_filters'] = status_filters
        filter_parameters = self.request.GET.copy()
        filter_parameters.pop('page', None)
        filter_parameters.pop(self.status_parameter,None)
        context['status_filter_query'] = filter_parameters.urlencode()

        return context



class InspectionCreateView(PermissionAwareSuccessMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'inspections.add_inspection'
    raise_exception = True
    model = Inspection
    form_class = InspectionCreateForm
    template_name = 'inspections/inspection_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.equipment = get_object_or_404(Equipment.objects
            .select_related(
                'customer_site',
                'customer_site__customer',
                'equipment_type',
                'equipment_type__specialty',
            ),
            slug=kwargs['equipment_slug'],
        )
        allowed_activity_types = get_allowed_inspection_types(self.equipment)
        if not allowed_activity_types:
            messages.warning(request, translate('A new activity cannot be created while the equipment is in its current status.'),)

            if request.user.has_perm('equipment.view_equipment'):
                return redirect('equipment:detail', equipment_slug=self.equipment.slug)
            return redirect('core:home')

        return super().dispatch(request,*args,**kwargs,)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['equipment'] = self.equipment
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment'] = self.equipment
        return context

    def form_valid(self, form):
        form.instance.equipment = self.equipment

        try:
            with transaction.atomic():
                response = super().form_valid(form)
                register_pending_inspection(self.object, actor=self.request.user)

        except ValidationError as error:
            self.object = None

            if hasattr(error, 'message_dict'):
                for messages in error.message_dict.values():
                    for message in messages:
                        form.add_error(None, message)
            else:
                for message in error.messages:
                    form.add_error(None, message)

            return self.form_invalid(form)

        return response

    def get_preferred_success_url(self):
        customer_site = self.equipment.customer_site
        customer_slug = customer_site.customer.slug
        site_slug = customer_site.slug
        return reverse('customers:site-details',kwargs={'customer_slug': customer_slug ,'site_slug': site_slug})

class InspectionAssignmentView(PermissionAwareSuccessMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'inspections.assign_inspection'
    raise_exception = True
    model = Inspection
    form_class = InspectionAssignmentForm
    template_name = 'inspections/inspection_assignment.html'
    context_object_name = 'inspection'
    success_url = reverse_lazy('inspections:list')

    def get_queryset(self):
        queryset = (super().get_queryset().filter( status__in=(Inspection.Status.PENDING, Inspection.Status.INTERRUPTED))
            .select_related('equipment', 'equipment__equipment_type', 'equipment__equipment_type__specialty')
            .prefetch_related('assigned_employees')
        )
        return filter_inspections_for_user(queryset, self.request.user)

    def form_valid(self, form):
        with transaction.atomic():
            previous_employees = get_assigned_employees_snapshot(self.object)
            response = super().form_valid(form)
            new_employees = get_assigned_employees_snapshot(self.object)
            previous_ids = {employee['id'] for employee in previous_employees}
            new_ids = {employee['id'] for employee in new_employees}

            if previous_ids != new_ids:
                record_inspection_event(
                    self.object,
                    InspectionHistory.EventType.ASSIGNED,
                    actor=self.request.user,
                    previous_status=self.object.status,
                    new_status=self.object.status,
                    description='Employee assignment changed.',
                    details={'previous_employees': previous_employees, 'new_employees': new_employees},
                )

        return response

class InspectionDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'inspections.view_inspection'
    raise_exception = True
    model = Inspection
    template_name = 'inspections/inspection_detail.html'
    context_object_name = 'inspection'

    def get_queryset(self):
        queryset = (super().get_queryset()
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__equipment_type__specialty',
                'equipment__customer_site',
                'equipment__customer_site__customer',
                'customer_contact',
            )
            .prefetch_related('assigned_employees')
        )
        return filter_inspections_for_user(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection_history'] = self.object.history.select_related('actor').order_by('-changed_at', '-pk')
        return context


class InspectionStartView(PermissionAwareSuccessMixin, PermissionRequiredMixin, InspectionActionMixin, FormView):
    permission_required = 'inspections.start_inspection'
    raise_exception = True
    form_class = InspectionStartForm
    template_name = 'inspections/inspection_start.html'

    def execute_action(self, form):
        start_inspection(self.inspection, actor=self.request.user)


class InspectionInterruptView(PermissionAwareSuccessMixin, PermissionRequiredMixin, InspectionActionMixin, FormView):
    permission_required = 'inspections.interrupt_inspection'
    raise_exception = True
    form_class = InspectionInterruptForm
    template_name = 'inspections/inspection_interrupt.html'

    def execute_action(self, form):
        interrupt_inspection(self.inspection,  actor=self.request.user)

class InspectionCompleteView(PermissionAwareSuccessMixin, PermissionRequiredMixin, InspectionActionMixin, FormView):
    permission_required = 'inspections.complete_inspection'
    raise_exception = True
    form_class = InspectionCompleteForm
    template_name = 'inspections/inspection_complete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inspection'] = self.inspection
        return kwargs

    def execute_action(self, form):
        result = form.cleaned_data['result']
        result_notes = form.cleaned_data['result_notes']
        complete_inspection(self.inspection, result= result, result_notes= result_notes, actor=self.request.user)

class InspectionCancelView(PermissionAwareSuccessMixin, PermissionRequiredMixin, InspectionActionMixin, FormView):
    permission_required = 'inspections.cancel_inspection'
    raise_exception = True
    form_class = InspectionCancelForm
    template_name = 'inspections/inspection_cancel.html'

    def execute_action(self, form):
        reason = form.cleaned_data['reason']
        cancel_inspection(self.inspection, reason=reason, actor=self.request.user)