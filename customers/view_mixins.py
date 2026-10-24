from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Customer, CustomerSite

class CustomerParentMixin:
    customer_url_kwarg = 'customer_pk'
    customer_context_name = 'customer'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)                                             #load the client
        self.customer = get_object_or_404(Customer,pk=kwargs[self.customer_url_kwarg],)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.customer_context_name] = self.customer
        return context

    def get_success_url(self):
        return reverse('customers:details',kwargs={'pk': self.customer.pk})

class CustomerSiteParentMixin(CustomerParentMixin):
    site_url_kwarg = 'site_pk'
    site_context_name = 'site'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.site = get_object_or_404(CustomerSite,pk=kwargs[self.site_url_kwarg],customer=self.customer)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.site_context_name] = self.site
        return context

    def get_success_url(self):
        return reverse('customers:site-details',kwargs={
                'customer_pk': self.customer.pk,
                'pk': self.site.pk,
                },
        )