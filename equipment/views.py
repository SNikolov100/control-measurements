from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from .forms import (EquipmentTypeEditForm,
                    EquipmentTypeCreateForm,
                    EquipmentTypeDeleteForm,
                    EquipmentCreateForm,
                    EquipmentEditForm,
                    )
from .models import Equipment, EquipmentType
from django.urls import reverse_lazy, reverse
from core.view_mixins import ConfirmedDeleteMixin, PaginationMixin, SearchMixin
from .view_mixins import EquipmentRegistrationMixin

class EquipmentTypeListView(SearchMixin, PaginationMixin, ListView):
    model = EquipmentType
    template_name = 'equipment/equipment_type_list.html'
    context_object_name = 'equipment_types'

    search_fields = (
        'name__icontains',
        'short_name__icontains',
        'specialty__code__icontains',
        'specialty__name__icontains',
        'specialty__short_name__icontains',
    )

    def get_queryset(self):
        return super().get_queryset().select_related('specialty')

class EquipmentTypeCreateView(CreateView):
    model = EquipmentType
    form_class = EquipmentTypeCreateForm
    template_name = 'equipment/equipment_type_create.html'
    success_url = reverse_lazy('equipment:types-list')

class EquipmentTypeEditView(UpdateView):
    model = EquipmentType
    form_class = EquipmentTypeEditForm
    template_name = 'equipment/equipment_type_edit.html'
    context_object_name = "equipment_type"
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

class EquipmentListView(SearchMixin, PaginationMixin, ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipment_items'

    search_fields = (
        "serial_number__icontains",
        "model_name__icontains",
        "equipment_type__name__icontains",
        "equipment_type__short_name__icontains",
        "customer_site__name__icontains",
        "customer_site__short_name__icontains",
    )

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
    slug_field = 'slug'
    slug_url_kwarg = 'equipment_slug'

    def get_success_url(self):
        customer_site = self.object.customer_site
        return reverse("customers:site-details",kwargs={
                "customer_slug": customer_site.customer.slug,
                "site_slug": customer_site.slug,
            },
        )

class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'
    slug_field = 'slug'
    slug_url_kwarg = 'equipment_slug'

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
