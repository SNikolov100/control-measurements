from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from equipment.models import Equipment
from .forms import InspectionCreateForm, InspectionAssignmentForm, InspectionStartForm, InspectionCompleteForm, \
    InspectionCancelForm
from .models import Inspection
from django.urls import reverse, reverse_lazy
from .services import complete_inspection, start_inspection, cancel_inspection


class InspectionListView(ListView):
    model = Inspection
    template_name = 'inspections/inspection_list.html'
    context_object_name = 'inspections'

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
            pk=kwargs['equipment_pk'],
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
        return reverse('equipment:detail', kwargs={'pk': self.equipment.pk})

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


class InspectionStartView(FormView):
    form_class = InspectionStartForm
    template_name = 'inspections/inspection_start.html'

    def dispatch(self, request, *args, **kwargs):
        self.inspection = get_object_or_404(Inspection.objects
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__equipment_type__specialty',
                'equipment__customer_site',
                'equipment__customer_site__customer',
            )
            .prefetch_related(
                'assigned_employees',
                'assigned_employees__specialties',
            ),
            pk=kwargs["pk"],
        )

        return super().dispatch(request,*args,**kwargs,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inspection"] = self.inspection
        return context

    def form_valid(self, form):
        try:
            start_inspection(self.inspection)

        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inspections:details',kwargs={'pk': self.inspection.pk},)

class InspectionCompleteView(FormView):
    form_class = InspectionCompleteForm
    template_name = 'inspections/inspection_complete.html'

    def dispatch(self, request, *args, **kwargs):
        self.inspection = get_object_or_404(
            Inspection.objects
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__customer_site',
                'equipment__customer_site__customer',
            )
            .prefetch_related(
                'assigned_employees',
            ),
            pk=kwargs['pk'],
        )

        return super().dispatch(request,*args,**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['inspection'] = self.inspection
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection'] = self.inspection
        return context

    def form_valid(self, form):
        try:
            complete_inspection(
                self.inspection,
                result=form.cleaned_data.get('result', ''),
                result_notes=form.cleaned_data['result_notes'],
            )

        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inspections:details',kwargs={'pk': self.inspection.pk})

class InspectionCancelView(FormView):
    form_class = InspectionCancelForm
    template_name = 'inspections/inspection_cancel.html'

    def dispatch(self, request, *args, **kwargs):
        self.inspection = get_object_or_404(Inspection.objects
            .select_related(
                'equipment',
                'equipment__equipment_type',
                'equipment__customer_site',
                'equipment__customer_site__customer',
            )
            .prefetch_related(
                'assigned_employees',
            ),
            pk=kwargs['pk'],
        )

        return super().dispatch(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inspection'] = self.inspection
        return context

    def form_valid(self, form):
        try:
            cancel_inspection(self.inspection, reason=form.cleaned_data['reason'])

        except ValidationError as error:
            for message in error.messages:
                form.add_error(None, message)

            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("inspections:details",kwargs={"pk": self.inspection.pk})