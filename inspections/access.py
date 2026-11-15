def filter_inspections_for_user(queryset, user):
    if not user.is_authenticated or not user.is_active:
        return queryset.none()

    if user.has_perm('inspections.view_all_inspections'):
        return queryset

    return queryset.filter(assigned_employees__user=user).distinct()