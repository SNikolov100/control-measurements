from django import template
from django.utils.translation import gettext_lazy as translate

register = template.Library()

STATUS_PRESENTATION = {
    'in_service': {'css_class': 'status-active','icon': '✓'},
    'waiting_inspection': {'css_class': 'status-warning','icon': '◷'},
    'under_inspection': {'css_class': 'status-in-progress','icon': '▶'},
    'under_repair': {'css_class': 'status-in-progress','icon': '⚙'},
    'waiting_reinspection': {'css_class': 'status-warning','icon': '↻'},
    'temporarily_suspended': {'css_class': 'status-neutral','icon': 'Ⅱ'},
    'decommissioned': {'css_class': 'status-inactive','icon': '×'},
    'pending': {'css_class': 'status-pending','icon': '◷'},
    'in_progress': {'css_class': 'status-in-progress','icon': '▶'},
    'completed': {'css_class': 'status-completed','icon': '✓'},
    'cancelled': {'css_class': 'status-cancelled','icon': '×'},
    'passed': {'css_class': 'status-passed','icon': '✓'},
    'failed': {'css_class': 'status-failed','icon': '!'},
    'active': {'css_class': 'status-active','icon': '✓','default_label': translate('Active')},
    'inactive': {'css_class': 'status-inactive','icon': '×','default_label': translate('Inactive')},
}

@register.inclusion_tag('components/status_badge.html')
def status_badge(status, label=None):
    normalized_status = str(status or '').strip()

    presentation = STATUS_PRESENTATION.get(normalized_status,
        {
            'css_class': 'status-neutral',
            'icon': '•',
        },
    )

    visible_label = (
        label
        or presentation.get('default_label')
        or normalized_status
        or '—'
    )

    return {
        'css_class': presentation['css_class'],
        'icon': presentation['icon'],
        'label': visible_label,
    }