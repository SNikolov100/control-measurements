from django import template
from django.utils.translation import gettext_lazy as translate

register = template.Library()

STATUS_PRESENTATION = {
    'in_service': {'css_class': 'status-active', 'icon': '✓', 'default_label': translate('In service')},
    'waiting_inspection': {'css_class': 'status-warning', 'icon': '◷', 'default_label': translate('Waiting for inspection')},
    'under_inspection': {'css_class': 'status-in-progress', 'icon': '▶', 'default_label': translate('Under inspection')},
    'under_repair': {'css_class': 'status-in-progress', 'icon': '⚙', 'default_label': translate('Under repair')},
    'waiting_reinspection': {'css_class': 'status-warning', 'icon': '↻', 'default_label': translate('Waiting for reinspection')},
    'temporarily_suspended': {'css_class': 'status-neutral', 'icon': 'Ⅱ', 'default_label': translate('Temporarily suspended')},
    'decommissioned': {'css_class': 'status-inactive', 'icon': '×', 'default_label': translate('Decommissioned')},
    'pending': {'css_class': 'status-pending', 'icon': '◷', 'default_label': translate('Pending')},
    'in_progress': {'css_class': 'status-in-progress', 'icon': '▶', 'default_label': translate('In progress')},
    'completed': {'css_class': 'status-completed', 'icon': '✓', 'default_label': translate('Completed')},
    'cancelled': {'css_class': 'status-cancelled', 'icon': '×', 'default_label': translate('Cancelled')},
    'passed': {'css_class': 'status-passed', 'icon': '✓', 'default_label': translate('Passed')},
    'failed': {'css_class': 'status-failed', 'icon': '!', 'default_label': translate('Failed')},
    'active': {'css_class': 'status-active', 'icon': '✓', 'default_label': translate('Active')},
    'inactive': {'css_class': 'status-inactive', 'icon': '×', 'default_label': translate('Inactive')},
    'primary': {'css_class': 'status-active', 'icon': '✓', 'default_label': translate('Primary contact')},
    'yes': {'css_class': 'status-active', 'icon': '✓', 'default_label': translate('Yes')},
    'no': {'css_class': 'status-neutral', 'icon': '•', 'default_label': translate('No')},
    'warning': {'css_class': 'status-warning', 'icon': '◷'},
    'neutral': {'css_class': 'status-neutral', 'icon': '•'},
}

@register.inclusion_tag('components/status_badge.html')
def status_badge(status, label=None):
    if isinstance(status, bool):
        normalized_status = 'active' if status else 'inactive'
    else:
        normalized_status = str(status or '').strip()
        lower_status = normalized_status.lower()
        if lower_status in ('true', 'active'):
            normalized_status = 'active'
        elif lower_status in ('false', 'inactive'):
            normalized_status = 'inactive'

    presentation = STATUS_PRESENTATION.get(
        normalized_status,
        {
            'css_class': 'status-neutral',
            'icon': '•',
        },
    )

    visible_label = (
        label
        or presentation.get('default_label')
        or normalized_status.replace('_', ' ').capitalize()
        or '—'
    )

    return {
        'css_class': presentation['css_class'],
        'icon': presentation['icon'],
        'label': visible_label,
    }