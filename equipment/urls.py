from django.urls import path, include

from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.EquipmentListView.as_view(), name='list'),
    path('create/', views.EquipmentCreateView.as_view(), name='create'),
    path('<str:equipment_slug>/', include([
        path('edit/', views.EquipmentEditView.as_view(), name='edit'),
        path('detail/', views.EquipmentDetailView.as_view(), name='detail'),
    ])),
    path('types/', include([
        path('', views.EquipmentTypeListView.as_view(), name='types-list'),
        path('create/', views.EquipmentTypeCreateView.as_view(), name='type-create'),
        path('<int:pk>/', include([
            path('edit/', views.EquipmentTypeEditView.as_view(), name='type-edit'),
            path('delete/', views.EquipmentTypeDeleteView.as_view(), name='type-delete'),
        ])),

    ])),



]