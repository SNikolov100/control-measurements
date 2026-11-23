from rest_framework import serializers
from .models import EquipmentType

class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = (
            'id',
            'name',
            'short_name',
            'specialty',
            'description',
            'default_interval_value',
            'default_interval_unit',
            'default_inspection_duration',
            'is_active',
        )
        read_only_fields = ('id',)