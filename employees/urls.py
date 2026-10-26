from django.urls import path, include

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='list'),
    path('create/', views.EmployeeCreateView.as_view(), name='create'),
    path('<int:pk>/', include([
        path('details/', views.EmployeeDetailView.as_view(), name='details'),
        path('edit/', views.EmployeeEditView.as_view(), name='edit'),
        path('activity-status/', views.EmployeeActivityStatusView.as_view(), name='activity-status'),

    ]))
]