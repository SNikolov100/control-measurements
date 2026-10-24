from django import forms
from .models import Equipment, EquipmentType, EquipmentStatusHistory
from core.base_forms import DeleteConfirmationForm

class EquipmentTypeBaseForm(forms.ModelForm):
    class Meta:
        model = EquipmentType
        fields = "__all__"

class EquipmentTypeCreateForm(EquipmentTypeBaseForm):
    ...

class EquipmentTypeEditForm(EquipmentTypeBaseForm):
    ...

class EquipmentTypeDeleteForm(DeleteConfirmationForm):
    ...

class EquipmentBaseForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = (
            'customer_site',
            'equipment_type',
            'model_name',
            'serial_number',
            'inventory_number',
            'inspection_interval_value',
            'inspection_interval_unit',
            'estimated_inspection_duration',
            'notes',
        )

class EquipmentCreateForm(EquipmentBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['inspection_interval_value'].required = False
        self.fields['inspection_interval_unit'].required = False
        self.fields['estimated_inspection_duration'].required = False

    def clean(self):
        cleaned_data = super().clean()
        equipment_type = cleaned_data.get('equipment_type')

        if equipment_type is None:
            return cleaned_data

        if not cleaned_data.get('inspection_interval_value'):
            cleaned_data['inspection_interval_value'] = equipment_type.default_interval_value

        if not cleaned_data.get('inspection_interval_unit'):
            cleaned_data['inspection_interval_unit'] = equipment_type.default_interval_unit

        if not cleaned_data.get('estimated_inspection_duration'):
            cleaned_data['estimated_inspection_duration'] = equipment_type.default_inspection_duration

        return cleaned_data

class EquipmentEditForm(EquipmentBaseForm):
    ...


class CustomerSiteEquipmentCreateForm(EquipmentCreateForm):
    class Meta(EquipmentCreateForm.Meta):
        exclude = ['customer_site']

    def __init__(self, *args, **kwargs):
        customer_site = kwargs.pop('customer_site', None)
        super().__init__(*args, **kwargs)
        if customer_site is not None:
            self.instance.customer_site = customer_site