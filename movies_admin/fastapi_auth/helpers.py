# django_app/auth/helpers.py
from .token_client import authenticated_request

def get_current_user(request):
    resp = authenticated_request(request, "GET", "/auth/me")

    if resp.status_code != 200:
        return None

    return resp.json()
