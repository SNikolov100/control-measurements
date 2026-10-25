from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Inspection


class InspectionActionMixin:
    inspection_url_kwarg = 'pk'
    inspection_context_name = 'inspection'

    def get_inspection_queryset(self):
        return (Inspection.objects
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
                'assigned_employees__specialties',
            )
        )

    def setup(self, request, *args, **kwargs):          #find current inspection before Post and Get
        super().setup(request, *args, **kwargs)
        self.inspection = get_object_or_404(self.get_inspection_queryset(), pk=kwargs[self.inspection_url_kwarg],)

    def get_context_data(self, **kwargs):               # for templates
        context = super().get_context_data(**kwargs)
        context[self.inspection_context_name] = self.inspection
        return context

    def add_validation_error_to_form(self,form,error):  #copy and paste errors in form
        for message in error.messages:
            form.add_error(None, message)

    def execute_action(self, form):                     #Rice error if we don't use it in views
        raise NotImplementedError('Inspection action views must implement execute_action().')

    def form_valid(self, form):
        try:
            self.execute_action(form)

        except ValidationError as error:
            self.add_validation_error_to_form(form, error,)
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('inspections:list')
