from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .forms import CustomerCreateView, CustomerEditView, CustomerSiteCreateForm, CustomerSiteEditForm
from .models import Customer, CustomerSite, CustomerContact

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
