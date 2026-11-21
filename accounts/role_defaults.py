from django.contrib.auth.models import Group, Permission
from django.db import transaction

READ = ('view',)
FULL = ('view', 'add', 'change', 'delete')

ROLE_PERMISSIONS = {
    'Employee': {
        'customers.customer': READ,
        'customers.customersite': READ,
        'customers.customercontact': READ,
        'employees.employee': READ,
        'equipment.equipmenttype': READ,
        'equipment.equipment': FULL,
        'equipment.equipmentstatushistory': READ,
        'inspections.inspection': READ,
    },
    'Operator': {
        'customers.customer': FULL,
        'customers.customersite': FULL,
        'customers.customercontact': FULL,
        'employees.employee': READ,
        'employees.employeehistory': READ,
        'equipment.equipmenttype': FULL,
        'equipment.equipment': FULL,
        'equipment.equipmentstatushistory': READ,
        'inspections.inspection': FULL,
    },
}
ROLE_CUSTOM_PERMISSIONS = {
    'Employee':
        {'inspections.inspection': ('start_inspection', 'complete_inspection')},
    'Operator': {
        'inspections.inspection': (
            'view_all_inspections',
            'assign_inspection',
            'start_inspection',
            'complete_inspection',
            'cancel_inspection',
        ),
    },
}


def create_default_groups(sender, using, **kwargs):
    role_permissions = {}

    for role_name in ROLE_PERMISSIONS:
        required = set()

        for model_path, actions in ROLE_PERMISSIONS[role_name].items():
            app_label, model_name = model_path.split('.')

            for action in actions:
                required.add((app_label, model_name, f'{action}_{model_name}'))

        for model_path, codenames in ROLE_CUSTOM_PERMISSIONS[role_name].items():
            app_label, model_name = model_path.split('.')

            for codename in codenames:
                required.add((app_label, model_name, codename))

        role_permissions[role_name] = required

    all_required = set().union(*role_permissions.values())
    available = {
        (permission.content_type.app_label, permission.content_type.model, permission.codename): permission.pk
        for permission in (Permission.objects.using(using)
            .select_related('content_type')
            .filter(content_type__app_label__in={item[0] for item in all_required})
        )
    }

    if not all_required.issubset(available):
        return

    with transaction.atomic(using=using):
        for role_name, required in role_permissions.items():
            group, created = Group.objects.db_manager(using).get_or_create(name=role_name)

            if created:
                group.permissions.set([available[item] for item in required])