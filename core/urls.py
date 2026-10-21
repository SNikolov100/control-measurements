from django.urls import path, include

from . import views

app_name = 'core'

urlpatterns = [
    path('specialties/', include([
        path('', views.specialty_list, name='specialty-list'),
        path('create/', views.SpecialtyCreateView.as_view(), name='specialty-create'),
        path('<int:pk>/', include([
            path('edit/', views.SpecialtyEditView.as_view(), name='specialty-edit'),
            path('delete/', views.SpecialtyDeleteView.as_view(), name='specialty-delete'),
        ])),
    ])),
]
