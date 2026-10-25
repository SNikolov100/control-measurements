from django.urls import include, path
from . import views

app_name = "customers"

urlpatterns = [
    path("",views.CustomerListView.as_view(),name="list",),
    path("create/",views.CustomerCreateView.as_view(),name="create",),
    path("<str:customer_slug>/",include([
            path("",views.CustomerDetailView.as_view(),name="details",),
            path("edit/",views.CustomerEditView.as_view(),name="edit",),
            path("sites/",include([
                    path("create/",views.CustomerSiteCreateView.as_view(),name="site-create",),
                    path("<str:site_slug>/",include([
                            path("details/",views.CustomerSiteDetailView.as_view(),name="site-details",),
                            path("edit/",views.CustomerSiteEditView.as_view(),name="site-edit",),
                            path("equipment/create/",views.CustomerSiteEquipmentCreateView.as_view(),name="site-equipment-create",),
                            path("contacts/",include([
                                  path("create/",views.CustomerContactCreateView.as_view(),name="contact-create",),
                                  path("<int:pk>/",include([
                                        path("details/",views.CustomerContactDetailView.as_view(),name="contact-details",),
                                        path("edit/",views.CustomerContactEditView.as_view(),name="contact-edit",),
                                        path("delete/",views.CustomerContactDeleteView.as_view(),name="contact-delete",),
                                  ])),
                            ])),
                    ])),
            ])),
    ])),
]