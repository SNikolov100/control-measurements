from rest_framework import generics, mixins, filters
from rest_framework.permissions import IsAuthenticated
from .models import EquipmentType
from .serializers import EquipmentTypeSerializer
from .api_permissions import CanManageEquipmentTypes
from django.db.models.deletion import ProtectedError
from django.utils.translation import gettext_lazy as translate
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from .api_pagination import EquipmentTypePagination

class EquipmentTypeListCreateAPIView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, CanManageEquipmentTypes]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ('name', 'short_name', 'specialty__code', 'specialty__name', 'specialty__short_name')
    filterset_fields = ('specialty', 'is_active', 'default_interval_unit')
    ordering_fields = ('name', 'short_name', 'specialty__name', 'default_interval_value', 'default_inspection_duration', 'is_active')
    ordering = ('name',)
    pagination_class = EquipmentTypePagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class EquipmentTypeDetailAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer
    permission_classes = [IsAuthenticated, CanManageEquipmentTypes]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        error_message = translate('This equipment type cannot be deleted because concrete equipment items use it. Deactivate the equipment type instead.')
        if instance.equipment_items.exists():
            raise ValidationError({'detail': error_message})

        try:
            super().perform_destroy(instance)
        except ProtectedError as exc:
            raise ValidationError({'detail': error_message}) from exc