from django.db.models import ProtectedError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView
from .forms import (SpecialtyCreateForm, SpecialtyEditForm,
                    SpecialtyDeleteForm, CompanySettingsForm,
                    SystemSettingsForm)

from .models import Specialty, CompanySettings, SystemSettings
from .view_mixins import SingleRecordFormViewMixin

def home(request: HttpRequest) -> HttpResponse:
    return render(request,"core/home.html")

def specialty_list(request: HttpRequest) ->HttpResponse:
    specialties = Specialty.objects.all()
    context = {
        "specialties": specialties,
    }
    return render(request, "core/specialty_list.html", context)

class SpecialtyCreateView(CreateView):
    model = Specialty
    form_class = SpecialtyCreateForm
    template_name = 'core/specialty_create.html'
    success_url = reverse_lazy('core:specialty-list')

class SpecialtyEditView(UpdateView):
    model = Specialty
    form_class = SpecialtyEditForm
    template_name = 'core/specialty_edit.html'
    success_url = reverse_lazy('core:specialty-list')

class SpecialtyDeleteView(DeleteView):
    model = Specialty
    form_class = SpecialtyDeleteForm
    context_object_name = 'specialty'
    template_name = 'core/specialty_delete.html'
    success_url = reverse_lazy('core:specialty-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        used_by_equipment_types = self.object.equipment_types.exists()
        used_by_employees = self.object.employees.exists()

        if used_by_equipment_types or used_by_employees:
            context = self.get_context_data(form=form)
            context["deletion_error"] = "This specialty cannot be deleted because it is currently in use. Deactivate it instead."
            context["deletion_blocked"] = True
            return self.render_to_response(context)

        try:
            return super().form_valid(form)

        except ProtectedError:
            context = self.get_context_data(form=form)
            context["deletion_error"] = "This specialty cannot be deleted because protected related records exist."
            context["deletion_blocked"] = True
            return self.render_to_response(context)

class CompanySettingsView(SingleRecordFormViewMixin, FormView):
    model = CompanySettings
    form_class = CompanySettingsForm
    template_name = 'core/company_settings.html'
    success_url = reverse_lazy('core:home')

class SystemSettingsView(SingleRecordFormViewMixin, FormView):
    model = SystemSettings
    form_class = SystemSettingsForm
    template_name = 'core/system_settings.html'
    success_url = reverse_lazy('core:home')
