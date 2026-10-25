from django.urls import path, include
from . import views

app_name = 'inspections'

urlpatterns = [
    path('', views.InspectionListView.as_view(), name='list'),
    path('<str:equipment_slug>/create/', views.InspectionCreateView.as_view(), name='create'),
    path('<int:pk>/', include([
        path('assign/', views.InspectionAssignmentView.as_view(), name='assign'),
        path('details/', views.InspectionDetailView.as_view(), name='details'),
        path('start/', views.InspectionStartView.as_view(), name='start'),
        path('complete/', views.InspectionCompleteView.as_view(), name='complete'),
        path('cancel/', views.InspectionCancelView.as_view(), name='cancel'),
    ])),
]