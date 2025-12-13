from django.conf import settings
from django.shortcuts import redirect

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access = request.session.get("access")
        refresh = request.session.get("refresh")

        # If access token is missing → redirect to login
        if not access:
            return redirect("login")

        # Optional: attach access token to request object
        request.jwt_access = access

        return self.get_response(request)
