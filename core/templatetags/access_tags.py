from django import template
from accounts.permissions import can_access_view

register = template.Library()

@register.simple_tag(takes_context=True)
def can_access(context, view_name, method='GET'):
    request = context.get('request')
    return bool(request
                and
                can_access_view(request.user, view_name, method, access_state=getattr(request, 'access_state', None)))

class AccessNode(template.Node):
    def __init__(self, view_name, allowed, denied):
        self.view_name, self.allowed, self.denied = view_name, allowed, denied

    def render(self, context):
        permitted = can_access(context, self.view_name.resolve(context))
        return (self.allowed if permitted else self.denied).render(context)


@register.tag('if_can_access')
def if_can_access(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError('if_can_access requires one route name')

    view_name = parser.compile_filter(bits[1])
    allowed = parser.parse(('else', 'endif_can_access'))
    end = parser.next_token()
    denied = template.NodeList()
    if end.contents == 'else':
        denied = parser.parse(('endif_can_access',))
        parser.delete_first_token()

    return AccessNode(view_name, allowed, denied)
