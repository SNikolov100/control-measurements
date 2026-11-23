from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .access import get_access_state
from .permissions import PUBLIC_VIEWS, can_access_view
from rest_framework.views import APIView


class AccessControlMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        api_view_class = getattr(view_func, 'cls', None)
        if isinstance(api_view_class, type) and issubclass(api_view_class, APIView):
            return None

        view_name = request.resolver_match.view_name
        request.access_state = get_access_state(request.user)
        if view_name in PUBLIC_VIEWS:
            return None

        if request.access_state == 'anonymous':
            return redirect_to_login(request.get_full_path())

        if can_access_view(request.user, view_name, request.method, access_state=request.access_state):
            return None

        if request.access_state != 'ready':
            return redirect('core:home')

        raise PermissionDenied
