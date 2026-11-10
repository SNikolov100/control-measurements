from django import template

register = template.Library()


@register.inclusion_tag('components/form_field.html')
def render_field(field, label=None, optional_label=None, css_class=None, is_checkbox=None):

    if field is None:
        return {'field': None}

    widget_type = getattr(field, 'widget_type', None)
    input_type = getattr(
        getattr(
            getattr(field, 'field', None),
            'widget', None),
        'input_type', None
    )

    computed_is_checkbox = is_checkbox
    if computed_is_checkbox is None:
        computed_is_checkbox = widget_type == 'checkboxinput' or input_type == 'checkbox'

    return {
        'field': field,
        'label': label,
        'optional_label': optional_label,
        'css_class': css_class,
        'is_checkbox': computed_is_checkbox,
    }
