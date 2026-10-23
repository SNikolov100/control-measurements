from django import forms
from customers.models import CustomerContact
from employees.models import Employee
from .models import Inspection


class InspectionBaseForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = (
            'inspection_type',
            'received_at',
            'due_date',
            'planned_start',
            'estimated_duration',
            'notes',
        )


class InspectionCreateForm(InspectionBaseForm):
    def __init__(self, *args, **kwargs):
        equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
        self.equipment = equipment
        self.fields['estimated_duration'].required = False

        # if equipment is None:
        #     self.fields['customer_contact'].queryset = CustomerContact.objects.none()
        #     return

        self.instance.equipment = equipment

    def clean_estimated_duration(self):
        estimated_duration = self.cleaned_data.get('estimated_duration')

        if estimated_duration:
            return estimated_duration

        return self.equipment.estimated_inspection_duration

class InspectionAssignmentForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['assigned_employees']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.equipment_id:
            self.fields['assigned_employees'].queryset = Employee.objects.none()
            return

        required_specialty = self.instance.equipment.equipment_type.specialty
        get_assigned_employees = Employee.objects.filter(is_active=True, specialties=required_specialty).distinct()
        self.fields['assigned_employees'].queryset = get_assigned_employees

class InspectionStartForm(forms.Form):
    ...

class InspectionCompleteForm(forms.Form):
    result = forms.ChoiceField(
        required=False,
        choices=Inspection.Result.choices,
        label='Result',
    )

    result_notes = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label='Result notes',
    )

    def __init__(self, *args, inspection=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inspection = inspection

        if inspection and inspection.inspection_type == Inspection.InspectionType.REPAIR:
            self.fields.pop('result')

    def clean(self):
        cleaned_data = super().clean()

        if self.inspection is None:
            return cleaned_data

        result = cleaned_data.get('result')
        result_notes = cleaned_data.get('result_notes', '').strip()

        if result == Inspection.Result.FAILED and not result_notes:
            self.add_error('result_notes','Result notes are required for a failed activity.',)

        if self.inspection.inspection_type == Inspection.InspectionType.REPAIR and not result_notes:
            self.add_error('result_notes','Describe the work performed during the repair.',)

        return cleaned_data

class InspectionCancelForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea,
        label='Cancellation reason',
    )