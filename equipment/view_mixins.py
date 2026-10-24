from django.db import transaction
from django.utils.translation import gettext_lazy as translate
from .models import EquipmentStatusHistory

class EquipmentRegistrationMixin:
    initial_history_reason = translate('Equipment registered.')

    def get_initial_history_reason(self):
        return self.initial_history_reason

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            EquipmentStatusHistory.objects.create(
                equipment=self.object,
                previous_status='',
                new_status=self.object.status,
                reason=self.get_initial_history_reason(),
            )

        return response
