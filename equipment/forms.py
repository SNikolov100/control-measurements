from django import forms
from .models import Equipment, EquipmentType, EquipmentStatusHistory

class EquipmentTypeBaseForm(forms.ModelForm):
    class Meta:
        model = EquipmentType
        fields = "__all__"

class EquipmentTypeCreateForm(EquipmentTypeBaseForm):
    ...

class EquipmentTypeEditForm(EquipmentTypeBaseForm):
    ...

class EquipmentTypeDeleteForm(EquipmentTypeBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = True

class EquipmentBaseForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = (
            "customer_site",
            "equipment_type",
            "model_name",
            "serial_number",
            "inventory_number",
            "inspection_interval_value",
            "inspection_interval_unit",
            "estimated_inspection_duration",
            "notes",
        )

class EquipmentListForm(EquipmentBaseForm):
    ...

class EquipmentCreateForm(EquipmentBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["inspection_interval_value"].required = False
        self.fields["inspection_interval_unit"].required = False
        self.fields["estimated_inspection_duration"].required = False

    def clean(self):
        cleaned_data = super().clean()
        equipment_type = cleaned_data.get("equipment_type")

        if equipment_type is None:
            return cleaned_data

        if not cleaned_data.get("inspection_interval_value"):
            cleaned_data["inspection_interval_value"] = equipment_type.default_interval_value

        if not cleaned_data.get("inspection_interval_unit"):
            cleaned_data["inspection_interval_unit"] = equipment_type.default_interval_unit

        if not cleaned_data.get("estimated_inspection_duration"):
            cleaned_data["estimated_inspection_duration"] = equipment_type.default_inspection_duration

        return cleaned_data

class EquipmentEditForm(EquipmentBaseForm):
    ...

class EquipmentStatusChangeForm(forms.Form):
    new_status = forms.ChoiceField(
        label="New status",
    )
    reason = forms.CharField(
        max_length=255,
        label="Reason",
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Notes",
    )
    def __init__(self, *args, equipment: Equipment, **kwargs,):
        super().__init__(*args, **kwargs)
        self.equipment = equipment
        self.fields["new_status"].choices = [
            (value, label)
            for value, label in Equipment.Status.choices
            if value != equipment.status
        ]