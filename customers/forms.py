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

class CustomerContactBaseForm(forms.ModelForm):
    class Meta:
        model = CustomerContact
        exclude = ['site']

    def __init__(self, *args, site=None, **kwargs):
        super().__init__(*args, **kwargs)

        if site is not None:
            self.instance.site = site

class CustomerContactCreateForm(CustomerContactBaseForm):
    ...

class CustomerContactEditForm(CustomerContactBaseForm):
    ...
class CustomerContactDeleteForm(forms.Form):
    ...