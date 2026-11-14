from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .access import get_access_state
from django.core.exceptions import PermissionDenied

class AccessControlMiddleware(MiddlewareMixin):
    public_views = {
        'accounts:login',
        'accounts:register',
        'accounts:registration_pending',
        'accounts:logout',
        'public:contacts',
        'public:about',
    }

    ready_view_permissions = {
        'customers:list': 'customers.view_customer',
        'customers:create': 'customers.add_customer',
        'customers:details': 'customers.view_customer',
        'customers:edit': 'customers.change_customer',
        'customers:site-create': 'customers.add_customersite',
        'customers:site-details': 'customers.view_customersite',
        'customers:site-edit': 'customers.change_customersite',
        'customers:contact-create': 'customers.add_customercontact',
        'customers:contact-details': 'customers.view_customercontact',
        'customers:contact-edit': 'customers.change_customercontact',
        'customers:contact-delete': 'customers.delete_customercontact',
        'customers:site-equipment-create': 'equipment.add_equipment',
        'equipment:list': 'equipment.view_equipment',
        'equipment:create': 'equipment.add_equipment',
        'equipment:detail': 'equipment.view_equipment',
        'equipment:edit': 'equipment.change_equipment',
        'equipment:types-list': 'equipment.view_equipmenttype',
        'equipment:type-create': 'equipment.add_equipmenttype',
        'equipment:type-edit': 'equipment.change_equipmenttype',
        'equipment:type-delete': 'equipment.delete_equipmenttype',
        'employees:list': 'employees.view_employee',
        'employees:details': 'employees.view_employee',
        'inspections:list': 'inspections.view_inspection',
        'inspections:details': 'inspections.view_inspection',
        'inspections:create': 'inspections.add_inspection',
        'inspections:assign': 'inspections.change_inspection',
        'inspections:start': 'inspections.change_inspection',
        'inspections:complete': 'inspections.change_inspection',
        'inspections:cancel': 'inspections.change_inspection',
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_name = request.resolver_match.view_name
        access_state = get_access_state(request.user)
        request.access_state = access_state
        if view_name in self.public_views:
            return None

        if access_state == 'anonymous':
            return redirect_to_login(request.get_full_path(), login_url=reverse('accounts:login'),)

        if view_name == "accounts:profile_create" and access_state == "profile_required":
            return None

        if view_name == "core:home":
            return None

        if access_state != "ready":
            return redirect("core:home")

        if request.user.is_superuser:
            return None

        required_permission = self.ready_view_permissions.get(view_name)
        if required_permission and request.user.has_perm(required_permission):
            return None

        raise PermissionDenied