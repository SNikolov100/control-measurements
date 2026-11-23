from django.urls import path
from accounts.api_views import ReadyTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from equipment.api_views import EquipmentTypeListCreateAPIView, EquipmentTypeDetailAPIView

urlpatterns = [
    path('token/', ReadyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('equipment-types/', EquipmentTypeListCreateAPIView.as_view(), name='api-equipment-type-list'),
    path('equipment-types/<int:pk>/', EquipmentTypeDetailAPIView.as_view(), name='api-equipment-type-detail'),

]