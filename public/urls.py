from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
]