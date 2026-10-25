from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, ListView
from .forms import (SpecialtyCreateForm, SpecialtyEditForm,
                    SpecialtyDeleteForm, CompanySettingsForm,
                    SystemSettingsForm)

from .models import Specialty, CompanySettings, SystemSettings
from .view_mixins import SingleRecordFormViewMixin, ConfirmedDeleteMixin, PaginationMixin, SearchMixin

def home(request: HttpRequest) -> HttpResponse:
    return render(request,"core/home.html")

class SpecialtyListView(SearchMixin, PaginationMixin, ListView):
    model = Specialty
    template_name = 'core/specialty_list.html'
    context_object_name = 'specialties'

    search_fields = (
        'code__icontains',
        'name__icontains',
        'short_name__icontains',
    )


class SpecialtyCreateView(CreateView):
    model = Specialty
    form_class = SpecialtyCreateForm
    template_name = 'core/specialty_create.html'
    success_url = reverse_lazy('core:specialty-list')

class SpecialtyEditView(UpdateView):
    model = Specialty
    form_class = SpecialtyEditForm
    template_name = 'core/specialty_edit.html'
    context_object_name = "specialty"
    success_url = reverse_lazy('core:specialty-list')

class SpecialtyDeleteView(ConfirmedDeleteMixin, DeleteView):
    model = Specialty
    form_class = SpecialtyDeleteForm
    context_object_name = 'specialty'
    template_name = 'core/specialty_delete.html'
    success_url = reverse_lazy('core:specialty-list')
    deletion_error_message = "This specialty cannot be deleted because it is currently in use. Deactivate it instead."

    def is_deletion_blocked(self):
        return self.object.equipment_types.exists() or self.object.employees.exists()


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
