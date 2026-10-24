from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .forms import (EquipmentTypeEditForm,
                    EquipmentTypeCreateForm,
                    EquipmentTypeDeleteForm,
                    EquipmentCreateForm,
                    EquipmentEditForm,
                    )
from .models import Equipment, EquipmentType
from django.urls import reverse_lazy
from core.view_mixins import ConfirmedDeleteMixin
from .view_mixins import EquipmentRegistrationMixin


class EquipmentTypeListView(ListView):
    model = EquipmentType
    template_name = 'equipment/equipment_type_list.html'
    context_object_name = 'equipment_types'

class EquipmentTypeCreateView(CreateView):
    model = EquipmentType
    form_class = EquipmentTypeCreateForm
    template_name = 'equipment/equipment_type_create.html'
    success_url = reverse_lazy('equipment:types-list')

class EquipmentTypeEditView(UpdateView):
    model = EquipmentType
    form_class = EquipmentTypeEditForm
    template_name = 'equipment/equipment_type_edit.html'
    success_url = reverse_lazy('equipment:types-list')

class EquipmentTypeDeleteView(ConfirmedDeleteMixin, DeleteView):
    model = EquipmentType
    form_class = EquipmentTypeDeleteForm
    context_object_name = 'equipment_type'
    template_name = 'equipment/equipment_type_delete.html'
    success_url = reverse_lazy('equipment:types-list')
    deletion_error_message = (
        'This equipment type cannot be deleted because concrete equipment items use it. '
        'Deactivate the equipment type instead.'
    )

    def is_deletion_blocked(self):
        return self.object.equipment_items.exists()

class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipment_items'

    def get_queryset(self):
        return (super().get_queryset().select_related(
                "customer_site",
                "customer_site__customer",
                "equipment_type",
                "equipment_type__specialty",
                )
        )

class EquipmentCreateView(EquipmentRegistrationMixin, CreateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'equipment/equipment_create.html'
    success_url = reverse_lazy('equipment:list')

class EquipmentEditView(UpdateView):
    model = Equipment
    form_class = EquipmentEditForm
    context_object_name = 'equipment'
    template_name = 'equipment/equipment_edit.html'
    success_url = reverse_lazy('equipment:list')

class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'

    def get_queryset(self):
        return (super().get_queryset().select_related(
                "customer_site",
                "customer_site__customer",
                "equipment_type",
                "equipment_type__specialty",
            )
            .prefetch_related(
                "status_history",
            )
        )
