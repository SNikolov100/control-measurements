from django.db.models import OuterRef, Subquery
from inspections.models import Inspection


def with_current_validity(queryset):
    latest_validity = (Inspection.objects
        .filter(
            equipment_id=OuterRef('pk'),
            status=Inspection.Status.COMPLETED,
            result=Inspection.Result.PASSED,
            valid_until__isnull=False,
        )
        .order_by('-actual_end', '-pk')
        .values('valid_until')[:1]
    )

    return queryset.annotate(current_valid_until=Subquery(latest_validity))