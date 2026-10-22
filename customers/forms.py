from django import forms

from .models import Customer, CustomerSite, CustomerContact

class CustomerBaseForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"

class CustomerCreateView(CustomerBaseForm):
    ...

class CustomerEditView(CustomerBaseForm):
    ...

class CustomerSiteBaseForm(forms.ModelForm):
    class Meta:
        model = CustomerSite
        exclude = ['customer']

class CustomerSiteCreateForm(CustomerSiteBaseForm):
    ...

class CustomerSiteEditForm(CustomerSiteBaseForm):
    ...
