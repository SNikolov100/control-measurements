from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.access import get_access_state


class CanManageEquipmentTypes(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.is_active or get_access_state(user) != 'ready':
            return False

        if request.method in SAFE_METHODS:
            return user.has_perm('equipment.view_equipmenttype')

        if request.method == 'POST':
            return user.has_perm('equipment.add_equipmenttype')

        if request.method in ('PUT', 'PATCH'):
            return user.has_perm('equipment.change_equipmenttype')

        if request.method == 'DELETE':
            return user.has_perm('equipment.delete_equipmenttype')

        return False
