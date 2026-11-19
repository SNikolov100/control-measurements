from .access import get_access_state

PUBLIC_VIEWS = {
    'accounts:login', 'accounts:register', 'accounts:registration_pending', 'accounts:logout',
    'public:contacts', 'public:about', 'accounts:verify_email',
}
ADMIN_VIEWS = {
    'accounts:pending_registrations', 'accounts:registration_decision',
    'employees:pending-requests', 'employees:review-request', 'employees:reconsider-request',
}
VIEW_PERMISSIONS = {
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
    'inspections:assign': 'inspections.assign_inspection',
    'inspections:start': 'inspections.start_inspection',
    'inspections:complete': 'inspections.complete_inspection',
    'inspections:cancel': 'inspections.cancel_inspection',
    'employees:create': 'employees.add_employee',
    'employees:edit': 'employees.change_employee',
    'employees:activity-status': 'employees.change_employee',
    'core:specialty-list': 'core.view_specialty',
    'core:specialty-create': 'core.add_specialty',
    'core:specialty-edit': 'core.change_specialty',
    'core:specialty-delete': 'core.delete_specialty',
}

SETTINGS_PERMISSIONS = {
    'core:company-settings': ('core.view_companysettings', 'core.change_companysettings'),
    'core:system-settings': ('core.view_systemsettings', 'core.change_systemsettings'),
}

def can_access_view(user, view_name, method='GET', *, access_state=None):
    if view_name in PUBLIC_VIEWS:
        return True

    if not user.is_authenticated or not user.is_active:
        return False

    if view_name == 'core:home':
        return True

    state = access_state if access_state is not None else get_access_state(user)
    if view_name == 'accounts:profile_create':
        return state == 'profile_required'

    if view_name == 'accounts:resend_verification_email':
        return state == 'email_verification_required' and method.upper() == 'POST'

    if state != 'ready':
        return False

    if user.is_superuser:
        return True

    if view_name in ADMIN_VIEWS or view_name.startswith('admin:'):
        return False

    if view_name in SETTINGS_PERMISSIONS:
        view_permission, change_permission = SETTINGS_PERMISSIONS[view_name]
        method = method.upper()

        if method == 'GET':
            return user.has_perm(view_permission) or user.has_perm(change_permission)

        if method == 'POST':
            return user.has_perm(change_permission)

        return False

    permission = VIEW_PERMISSIONS.get(view_name)
    return bool(permission and user.has_perm(permission))
