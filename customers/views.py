from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .forms import (
    CustomerCreateView, CustomerEditView,
    CustomerSiteCreateForm, CustomerSiteEditForm,
    CustomerContactCreateForm, CustomerContactEditForm, CustomerContactDeleteForm,
)
from .models import Customer, CustomerSite, CustomerContact
from django.db import transaction
from equipment.forms import CustomerSiteEquipmentCreateForm
from equipment.models import Equipment,EquipmentStatusHistory

class CustomerListView(ListView):
    model = Customer
    template_name = 'customer/customer_list.html'
    context_object_name = 'customers'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerCreateView
    template_name = 'customer/customer_create.html'
    success_url = reverse_lazy('customers:list')

class CustomerEditView(UpdateView):
    model = Customer
    form_class = CustomerEditView
    template_name = 'customer/customer_edit.html'
    success_url = reverse_lazy('customers:list')

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'
    context_object_name = 'customer'

    def get_queryset(self):
        return super().get_queryset().prefetch_related("sites")

class CustomerSiteCreateView(CreateView):
    model = CustomerSite
    form_class = CustomerSiteCreateForm
    template_name = 'customer/customer_site_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"])

        return super().dispatch(request,*args,**kwargs,)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context

    def form_valid(self, form):
        form.instance.customer = self.customer
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("customers:details",kwargs={"pk": self.customer.pk},)

class CustomerSiteEditView(UpdateView):
    model = CustomerSite
    form_class = CustomerSiteEditForm
    template_name = 'customer/customer_site_edit.html'
    context_object_name = 'site'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)
        return super().dispatch(request,*args,**kwargs,)

    def get_queryset(self):
        return super().get_queryset().filter(customer=self.customer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context

    def get_success_url(self):
        return reverse("customers:details",kwargs={"pk": self.customer.pk},)

class CustomerSiteDetailView(DetailView):
    model = CustomerSite
    template_name = 'customer/customer_site_detail.html'
    context_object_name = 'site'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"])
        return super().dispatch(request,*args,**kwargs,)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(customer=self.customer)
            .select_related("customer")
            .prefetch_related("contacts","equipment_items",)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context


class CustomerContactCreateView(CreateView):
    model = CustomerContact
    form_class = CustomerContactCreateForm
    template_name = 'customer/customer_contact_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)

        self.site = get_object_or_404(CustomerSite,pk=kwargs["site_pk"],customer=self.customer,)

        return super().dispatch(request,*args,**kwargs,)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["site"] = self.site
        return context

    def form_valid(self, form):
        form.instance.site = self.site
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("customers:site-details",kwargs={
            "customer_pk": self.customer.pk,
            "pk": self.site.pk,
        })

class CustomerContactEditView(UpdateView):
    model = CustomerContact
    form_class = CustomerContactEditForm
    template_name = 'customer/customer_contact_edit.html'
    context_object_name = 'contact'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)
        self.site = get_object_or_404(CustomerSite,pk=kwargs["site_pk"],customer=self.customer,)
        return super().dispatch(request,*args,**kwargs,)

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["site"] = self.site
        return context

    def get_success_url(self):
        return reverse("customers:site-details",kwargs={
                "customer_pk": self.customer.pk,
                "pk": self.site.pk,
            })

class CustomerContactDetailView(DetailView):
    model = CustomerContact
    template_name = "customer/customer_contact_detail.html"
    context_object_name = "contact"

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)
        self.site = get_object_or_404(CustomerSite,pk=kwargs["site_pk"],customer=self.customer,)
        return super().dispatch(request,*args,**kwargs,)

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site).select_related("site","site__customer",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["site"] = self.site
        return context

class CustomerContactDeleteView(DeleteView):
    model = CustomerContact
    form_class = CustomerContactDeleteForm
    template_name = 'customer/customer_contact_delete.html'
    context_object_name = 'contact'

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)
        self.site = get_object_or_404(CustomerSite,pk=kwargs["site_pk"],customer=self.customer,)
        return super().dispatch(request,*args,**kwargs,)

    def get_queryset(self):
        return super().get_queryset().filter(site=self.site)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["site"] = self.site
        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)

        except ProtectedError:
            context = self.get_context_data(form=form)
            context["deletion_blocked"] = True
            context["deletion_error"] = ("This contact cannot be deleted"
                                         " because it is used by one or more activities."
                                         " Deactivate the contact instead.")
            return self.render_to_response(context)

    def get_success_url(self):
        return reverse("customers:site-details",kwargs={
                "customer_pk": self.customer.pk,
                "pk": self.site.pk,
            })

class CustomerSiteEquipmentCreateView(CreateView):
    model = Equipment
    form_class = CustomerSiteEquipmentCreateForm
    template_name = "customer/customer_site_equipment_create.html"

    def dispatch(self, request, *args, **kwargs):
        self.customer = get_object_or_404(Customer,pk=kwargs["customer_pk"],)
        self.site = get_object_or_404(CustomerSite,pk=kwargs["site_pk"],customer=self.customer,)
        return super().dispatch(request,*args,**kwargs,)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["customer_site"] = self.site
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["site"] = self.site
        return context

    def form_valid(self, form):
        form.instance.customer_site = self.site

        with transaction.atomic():
            response = super().form_valid(form)
            EquipmentStatusHistory.objects.create(
                equipment=self.object,
                previous_status="",
                new_status=self.object.status,
                reason="Equipment registered.",
            )

        return response

    def get_success_url(self):
        return reverse("customers:site-details", kwargs={
                "customer_pk": self.customer.pk,
                "pk": self.site.pk,
            })
