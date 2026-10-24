from django.urls import path, include

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('settings/', include([
        path('company/', views.CompanySettingsView.as_view(), name='company-settings'),
        path('system/', views.SystemSettingsView.as_view(), name='system-settings'),
    ])),
    path('specialties/', include([
        path('', views.SpecialtyListView.as_view(), name='specialty-list'),
        path('create/', views.SpecialtyCreateView.as_view(), name='specialty-create'),
        path('<int:pk>/', include([
            path('edit/', views.SpecialtyEditView.as_view(), name='specialty-edit'),
            path('delete/', views.SpecialtyDeleteView.as_view(), name='specialty-delete'),
        ])),
    ])),
]
