from django.shortcuts import redirect
from django.urls import resolve

EXEMPT_URL_NAMES = {
    "auth:login",
    "auth:logout",
}

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            resolved = resolve(request.path_info)
            url_name = f"{resolved.app_name}:{resolved.url_name}"
        except Exception:
            url_name = None

        # Allow exempt URLs without auth
        if url_name in EXEMPT_URL_NAMES:
            return self.get_response(request)

        access = request.session.get("access")

        if not access:
            return redirect("auth:login")

        request.jwt_access = access
        return self.get_response(request)