from django import forms
from django.utils.translation import gettext_lazy as translate
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
        widgets = {
            "received_at": forms.DateTimeInput(
                attrs={'type': 'datetime-local',},
                format='%Y-%m-%dT%H:%M',
            ),
            'due_date': forms.DateInput(
                attrs={'type': 'date',},
                format="%Y-%m-%d",
            ),
            'planned_start': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'estimated_duration': forms.NumberInput(
                attrs={
                    'min': 1,
                    'placeholder': 'Leave empty to use the equipment default',
                },
            ),
            'notes': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Describe the requested activity, reported fault, or other relevant information.',
                },
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["received_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["due_date"].input_formats = ["%Y-%m-%d"]
        self.fields["planned_start"].input_formats = ["%Y-%m-%dT%H:%M"]


class InspectionCreateForm(InspectionBaseForm):
    def __init__(self, *args, **kwargs):
        equipment = kwargs.pop('equipment', None)
        super().__init__(*args, **kwargs)
        self.equipment = equipment
        self.fields['estimated_duration'].required = False
        if equipment is not None:
            self.instance.equipment = equipment

    def clean_estimated_duration(self):
        estimated_duration = self.cleaned_data.get('estimated_duration')

        if estimated_duration:
            return estimated_duration

        if self.equipment is None:
            raise forms.ValidationError(translate('Equipment is required to determine the estimated duration.'))

        return self.equipment.estimated_inspection_duration

    def clean(self):
        cleaned_data = super().clean()
        inspection_type = cleaned_data.get('inspection_type')
        notes = cleaned_data.get('notes', '').strip()

        if inspection_type == Inspection.InspectionType.REPAIR and not notes:
            self.add_error('notes',translate('Describe the fault or the reason for opening the repair activity.'))

        return cleaned_data


class InspectionAssignmentForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['assigned_employees']
        widgets = {'assigned_employees': forms.CheckboxSelectMultiple()}

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
        choices=Inspection.Result.choices,
        label=translate('Result'),
    )
    result_notes = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label=translate('Result notes'),
    )

    def __init__(self, *args, inspection=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.inspection = inspection

        if inspection and inspection.inspection_type == Inspection.InspectionType.REPAIR:
            self.fields.pop('result')
            self.fields['result_notes'].widget.attrs.update(
                {'placeholder': 'Describe the repair work performed, replaced components, and adjustments.'}
            )
        else:
            self.fields["result_notes"].widget.attrs.update(
                {'placeholder': 'Add final findings or describe the reason for a failed result.'}
            )

    def clean(self):
        cleaned_data = super().clean()

        if self.inspection is None:
            return cleaned_data

        result = cleaned_data.get('result')
        result_notes = cleaned_data.get('result_notes', '').strip()

        if result == Inspection.Result.FAILED and not result_notes:
            self.add_error('result_notes',translate('Describe why the activity failed.'),)

        if self.inspection.inspection_type == Inspection.InspectionType.REPAIR and not result_notes:
            self.add_error('result_notes',translate('Describe the work performed during the repair.'),)

        return cleaned_data

class InspectionCancelForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': 'Describe why the activity is being cancelled.',
            }
        ),
        label='Cancellation reason',
        help_text=translate('The reason will be stored with the cancelled activity.'),
        error_messages={'required': translate('Enter a reason for cancelling the activity.'),},
    )
