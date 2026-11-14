from django.contrib.auth.views import LogoutView
from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register/',views.AppUserRegistrationView.as_view(),name='register'),
    path('registration-pending/',views.RegistrationPendingView.as_view(),name='registration_pending'),
    path("pending-registrations/", views.PendingRegistrationsView.as_view(), name="pending_registrations"),
    path('login/', views.AppUserLoginView.as_view(), name='login'),
    path('registration/<int:pk>/<str:action>/', views.registration_decision, name="registration_decision"),
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile_create'),
]

