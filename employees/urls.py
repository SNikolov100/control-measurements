from django.urls import path, include

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.EmployeeListView.as_view(), name='list'),
    path('create/', views.EmployeeCreateView.as_view(), name='create'),
    path('requests/', include([
        path('pending/', views.PendingEmployeeRequestsView.as_view(), name='pending-requests'),
        path("<int:pk>/review/", views.EmployeeRequestReviewView.as_view(), name="review-request"),
        path("<int:pk>/reconsider/", views.reconsider_employee_request_view, name="reconsider-request"),
    ])),
    path('<int:pk>/', include([
        path('details/', views.EmployeeDetailView.as_view(), name='details'),
        path('edit/', views.EmployeeEditView.as_view(), name='edit'),
        path('activity-status/', views.EmployeeActivityStatusView.as_view(), name='activity-status'),

    ]))
]