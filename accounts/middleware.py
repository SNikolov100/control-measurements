from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .access import get_access_state

class AccessControlMiddleware(MiddlewareMixin):

    public_views = {
        'accounts:login',
        'accounts:register',
        'accounts:registration_pending',
        'accounts:logout',
        'public:contacts',
        'public:about',
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_name = request.resolver_match.view_name
        access_state = get_access_state(request.user)
        request.access_state = access_state
        if view_name in self.public_views:
            return None

        if access_state == 'anonymous':
            return redirect_to_login(request.get_full_path(), login_url=reverse('accounts:login'),)

        if view_name == "accounts:profile_create" and access_state == "profile_required":
            return None

        if access_state == "ready":
            return None

        if view_name == "core:home":
            return None

        return redirect("core:home")