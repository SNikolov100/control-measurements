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
        ])),
        path('<int:site_pk>/contacts/',include([
            path('create/', views.CustomerContactCreateView.as_view(), name='contact-create'),
            path('<int:pk>/', include([
                path('edit/', views.CustomerContactEditView.as_view(), name='contact-edit'),
                path('detail', views.CustomerContactDetailView.as_view(), name='contact-details'),
                path('delete', views.CustomerContactDeleteView.as_view(), name='contact-delete'),
            ])),
        ])),
    path('<int:site_pk>/equipment/create/', views.CustomerSiteEquipmentCreateView.as_view(), name='site-equipment-create'),

    ])),


]