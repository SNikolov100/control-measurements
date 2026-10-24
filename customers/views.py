from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .forms import (
    CustomerCreateForm, CustomerEditForm,
    CustomerSiteCreateForm, CustomerSiteEditForm,
    CustomerContactCreateForm, CustomerContactEditForm, CustomerContactDeleteForm,
)
from .models import Customer, CustomerSite, CustomerContact
from equipment.forms import CustomerSiteEquipmentCreateForm
from equipment.models import Equipment
from core.view_mixins import ConfirmedDeleteMixin
from .view_mixins import CustomerParentMixin, CustomerSiteParentMixin
from equipment.view_mixins import EquipmentRegistrationMixin

class CustomerListView(ListView):
    model = Customer
    template_name = 'customer/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerCreateForm
    template_name = 'customer/customer_create.html'
    success_url = reverse_lazy('customers:list')

class CustomerEditView(UpdateView):
    model = Customer
    form_class = CustomerEditForm
    template_name = 'customer/customer_edit.html'
    success_url = reverse_lazy('customers:list')

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'
    context_object_name = 'customer'

    def get_queryset(self):
        return super().get_queryset().prefetch_related("sites")

class CustomerSiteCreateView(CustomerParentMixin, CreateView):
    model = CustomerSite
    form_class = CustomerSiteCreateForm
    template_name = 'customer/customer_site_create.html'

    def form_valid(self, form):
        form.instance.customer = self.customer
        return super().form_valid(form)

class CustomerSiteEditView(CustomerParentMixin, UpdateView):
    model = CustomerSite
    form_class = CustomerSiteEditForm
    template_name = 'customer/customer_site_edit.html'
    context_object_name = 'site'

    def get_queryset(self):
        return super().get_queryset().filter(customer=self.customer)

class CustomerSiteDetailView(CustomerParentMixin, DetailView):
    model = CustomerSite
    template_name = 'customer/customer_site_detail.html'
    context_object_name = 'site'

    def get_queryset(self):
        return (super()
            .get_queryset()
            .filter(customer=self.customer)
            .select_related("customer")
            .prefetch_related("contacts","equipment_items",)
        )

class CustomerContactCreateView(CustomerSiteParentMixin, CreateView):
    model = CustomerContact
    form_class = CustomerContactCreateForm
    template_name = 'customer/customer_contact_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

    def form_valid(self, form):
        form.instance.site = self.site
        return super().form_valid(form)

class CustomerContactEditView(CustomerSiteParentMixin, UpdateView):
    model = CustomerContact
    form_class = CustomerContactEditForm
    template_name = 'customer/customer_contact_edit.html'
    context_object_name = 'contact'

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

class CustomerContactDetailView(CustomerSiteParentMixin, ConfirmedDeleteMixin, DetailView):
    model = CustomerContact
    template_name = 'customer/customer_contact_detail.html'
    context_object_name = 'contact'

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site).select_related('site','site__customer',)

class CustomerContactDeleteView(CustomerSiteParentMixin, ConfirmedDeleteMixin, DeleteView):
    model = CustomerContact
    form_class = CustomerContactDeleteForm
    template_name = 'customer/customer_contact_delete.html'
    context_object_name = 'contact'
    deletion_error_message = (
        'This contact cannot be deleted because it is used by one or more activities. Deactivate the contact instead.'
    )

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site)

class CustomerSiteEquipmentCreateView(CustomerSiteParentMixin, EquipmentRegistrationMixin, CreateView):
    model = Equipment
    form_class = CustomerSiteEquipmentCreateForm
    template_name = 'customer/customer_site_equipment_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer_site'] = self.site
        return kwargs

    def form_valid(self, form):
        form.instance.customer_site = self.site
        return super().form_valid(form)
