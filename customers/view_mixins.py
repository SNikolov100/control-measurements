from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Customer, CustomerSite

class CustomerParentMixin:
    customer_url_kwarg = 'customer_slug'
    customer_context_name = 'customer'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)                                             #load the client
        self.customer = get_object_or_404(Customer,slug=kwargs[self.customer_url_kwarg],)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.customer_context_name] = self.customer
        return context

    def get_success_url(self):
        return reverse('customers:details',kwargs={'customer_slug': self.customer.slug})

class CustomerSiteParentMixin(CustomerParentMixin):
    site_url_kwarg = 'site_slug'
    site_context_name = 'site'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        customer_site = CustomerSite.objects.select_related("customer",)
        self.site = get_object_or_404(
            customer_site,
            slug=kwargs[self.site_url_kwarg],
            customer=self.customer,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.site_context_name] = self.site
        return context

    def get_success_url(self):
        return reverse('customers:site-details',kwargs={
                'customer_slug': self.customer.slug,
                "site_slug": self.site.slug,
                },
        )