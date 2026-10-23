from django.db.models import ProtectedError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView
from .forms import (EquipmentTypeEditForm,
                    EquipmentTypeCreateForm,
                    EquipmentTypeDeleteForm,
                    EquipmentListForm,
                    EquipmentCreateForm,
                    EquipmentEditForm,
                    )
from .models import Equipment, EquipmentType, EquipmentStatusHistory
from django.urls import reverse_lazy, reverse


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

class EquipmentTypeDeleteView(DeleteView):
    model = EquipmentType
    form_class = EquipmentTypeDeleteForm
    context_object_name = 'equipment_type'
    template_name = 'equipment/equipment_type_delete.html'
    success_url = reverse_lazy('equipment:types-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        if self.object.equipment_items.exists():
            context = self.get_context_data(form=form)
            context["deletion_blocked"] = True
            context["deletion_error"] = ("This equipment type cannot be deleted because "
                "concrete equipment items use it. Deactivate the equipment type instead.")

            return self.render_to_response(context)

        try:
            return super().form_valid(form)

        except ProtectedError:
            context = self.get_context_data(form=form)
            context["deletion_blocked"] = True
            context["deletion_error"] = ("This equipment type cannot be deleted"
                                         " because protected related records exist.")

            return self.render_to_response(context)

class EquipmentListView(ListView):
    model = Equipment
    form_class = EquipmentListForm
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

class EquipmentCreateView(CreateView):
    model = Equipment
    form_class = EquipmentCreateForm
    template_name = 'equipment/equipment_create.html'
    success_url = reverse_lazy('equipment:list')

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            EquipmentStatusHistory.objects.create(
                equipment=self.object,
                previous_status="",
                new_status=self.object.status,
                reason="Equipment registered.",
            )

            return response

class EquipmentEditView(UpdateView):
    model = Equipment
    form_class = EquipmentEditForm
    context_object_name = 'equipment'
    template_name = 'equipment/equipment_edit.html'
    success_url = reverse_lazy('equipment:list')

class EquipmentDetailView(DeleteView):
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
