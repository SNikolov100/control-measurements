from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from equipment.models import Equipment
from .forms import InspectionCreateForm, InspectionAssignmentForm, InspectionStartForm, InspectionCompleteForm, InspectionCancelForm
from .models import Inspection
from django.urls import reverse, reverse_lazy
from .services import complete_inspection, start_inspection, cancel_inspection
from .view_mixins import InspectionActionMixin
from core.view_mixins import PaginationMixin, SearchMixin


class InspectionListView(SearchMixin, PaginationMixin, ListView):
    model = Inspection
    template_name = 'inspections/inspection_list.html'
    context_object_name = 'inspections'
    search_fields = (
        "equipment__serial_number__icontains",

        "equipment__model_name__icontains",
        "equipment__equipment_type__name__icontains",
        "equipment__equipment_type__short_name__icontains",
        "assigned_employees__full_name__icontains",
        "customer_contact__full_name__icontains",
    )

    search_distinct = True


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
        return queryset_result

class InspectionCreateView(CreateView):
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
        return super().form_valid(form)

    def get_success_url(self):
        customer_site = self.equipment.customer_site
        customer_slug = customer_site.customer.slug
        site_slug = customer_site.slug
        return reverse('customers:site-details',kwargs={'customer_slug': customer_slug ,'site_slug': site_slug},
        )

class InspectionAssignmentView(UpdateView):
    model = Inspection
    form_class = InspectionAssignmentForm
    template_name = 'inspections/inspection_assignment.html'
    context_object_name = 'inspection'
    success_url = reverse_lazy('inspections:list')

    def get_queryset(self):
        return (super()
            .get_queryset()
            .filter(status=Inspection.Status.PENDING)
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__equipment_type__specialty',
            )
            .prefetch_related(
                'assigned_employees',
            )
        )

class InspectionDetailView(DetailView):
    model = Inspection
    template_name = 'inspections/inspection_detail.html'
    context_object_name = 'inspection'

    def get_queryset(self):
        return (super()
            .get_queryset()
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__equipment_type__specialty',
                'equipment__customer_site',
                'equipment__customer_site__customer',
                'customer_contact',
            )
            .prefetch_related(
                'assigned_employees',
            )
        )


class InspectionStartView(InspectionActionMixin, FormView):
    form_class = InspectionStartForm
    template_name = 'inspections/inspection_start.html'

    def execute_action(self, form):
        start_inspection(self.inspection)

class InspectionCompleteView(InspectionActionMixin, FormView):
    form_class = InspectionCompleteForm
    template_name = 'inspections/inspection_complete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inspection'] = self.inspection
        return kwargs

    def execute_action(self, form):
        result = form.cleaned_data.get('result','')
        result_notes = form.cleaned_data['result_notes']
        complete_inspection(self.inspection, result= result, result_notes= result_notes,)

class InspectionCancelView(InspectionActionMixin, FormView):
    form_class = InspectionCancelForm
    template_name = 'inspections/inspection_cancel.html'

    def execute_action(self, form):
        reason = form.cleaned_data['reason']
        cancel_inspection(self.inspection, reason=reason,)