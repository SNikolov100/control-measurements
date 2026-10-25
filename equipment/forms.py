from django import forms
from .models import Equipment, EquipmentType
from core.base_forms import DeleteConfirmationForm
from django.utils.translation import gettext_lazy as translate

class EquipmentTypeBaseForm(forms.ModelForm):
    class Meta:
        model = EquipmentType
        fields = (
            'name',
            'short_name',
            'specialty',
            'description',
            'default_interval_value',
            'default_interval_unit',
            'default_inspection_duration',
            'is_active',
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "For example: Digital thermometer"},),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Describe the equipment type and its typical application.",
                },
            ),
            "default_interval_value": forms.NumberInput(
                attrs={
                    "min": 1,
                    "placeholder": "For example: 12",
                },
            ),
            "default_inspection_duration": forms.NumberInput(
                attrs={
                    "min": 1,
                    "placeholder": "For example: 60",
                },
            ),
        }
        help_texts = {
            "name": translate("Enter the full name of the equipment type."),
            "short_name": translate("Enter a shorter name for registers and activities."),
            "specialty": translate("Select the specialty required for this type of equipment."),
            "description": translate("Optional description of the equipment type."),
            "default_interval_value": translate("Default interval used when registering equipment of this type."),
            "default_interval_unit": translate("Select the unit for the default inspection interval."),
            "default_inspection_duration": translate("Default estimated activity duration in minutes."),
            "is_active": translate("Inactive equipment types remain visible but should not be used for new equipment registrations."),
        }
        error_messages = {
            "name": {
                "required": translate("Enter the equipment-type name."),
                "unique": translate("An equipment type with this name already exists."),
            },
            "specialty": {"required": translate("Select the required specialty.")},
            "default_interval_value": {
                "required": translate("Enter the default inspection interval."),
                "invalid": translate("Enter a valid default inspection interval."),
            },
            "default_interval_unit": {"required": translate("Select the default interval unit."),},
            "default_inspection_duration": {
                "required": translate("Enter the default activity duration."),
                "invalid": translate("Enter a valid duration in minutes."),
            },
        }

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
        widgets = {
            'model_name': forms.TextInput(attrs={'placeholder': 'For example: Model 100'}),
            'serial_number': forms.TextInput(attrs={'placeholder': 'For example: SN-2026-001'}),
            'inventory_number': forms.TextInput(attrs={'placeholder': 'For example: INV-001'}),
            'inspection_interval_value': forms.NumberInput(
                attrs={
                    'min': 1,
                    'placeholder': 'Leave empty to use the equipment-type default',
                }
            ),
            'estimated_inspection_duration': forms.NumberInput(
                attrs={
                    'min': 1,
                    'placeholder': 'Leave empty to use the equipment-type default',
                },
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Add relevant information about the equipment.',
                },
            ),
        }
        help_texts = {
            'customer_site': translate('Select the customer site to which the equipment belongs.'),
            'equipment_type': translate('Select the equipment type and specialty.'),
            'model_name': translate('Enter the manufacturer model when available.'),
            'serial_number': translate('Enter the unique manufacturer serial number.'),
            'inventory_number': translate('Enter an internal inventory number when available.'),
            'inspection_interval_value': translate('Leave empty to use the default value from the equipment type.'),
            'inspection_interval_unit': translate('Leave empty to use the default unit from the equipment type.'),
            'estimated_inspection_duration': translate(
                'Leave empty to use the default duration from the equipment type.'),
            'notes': translate('Optional additional information.'),
        }
        error_messages = {
            'customer_site': {'required': translate('Select the customer site.')},
            'equipment_type': {'required': translate('Select the equipment type.')},
            'serial_number': {
                'required': translate('Enter the equipment serial number.'),
                'unique': translate('Equipment with this serial number already exists.'),
            },
            'inventory_number': {'unique': translate('Equipment with this inventory number already exists.')},
        }

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop('customer_site', None)


class CustomerSiteEquipmentCreateForm(EquipmentCreateForm):
    def __init__(self, *args, **kwargs):
        customer_site = kwargs.pop('customer_site', None)
        super().__init__(*args, **kwargs)

        self.fields.pop('customer_site', None)

        if customer_site is not None:
            self.instance.customer_site = customer_site