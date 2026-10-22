from django.urls import path, include

from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='list'),
    path('create/', views.CustomerCreateView.as_view(), name='create'),
    path('<int:pk>/', include([
        path('', views.CustomerDetailView.as_view(), name='details'),
        path('edit/', views.CustomerEditView.as_view(), name='edit'),
    ])),
    path('<int:customer_pk>/sites/', include([
        path('create/', views.CustomerSiteCreateView.as_view(), name='site-create'),
        path('<int:pk>/', include([
            path('edit/', views.CustomerSiteEditView.as_view(), name='site-edit'),
            path('details/', views.CustomerSiteDetailView.as_view(), name='site-details'),
        ]))

    ])),


]