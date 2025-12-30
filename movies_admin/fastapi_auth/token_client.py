import requests
from django.conf import settings
from django.shortcuts import redirect

API_BASE = settings.AUTH_API_URL

def authenticated_request(request, method, path, **kwargs):
    access = request.session.get("access")
    refresh = request.session.get("refresh")

    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {access}"

    resp = requests.request(method, f"{API_BASE}{path}", headers=headers, **kwargs)

    # If access token expired → refresh
    if resp.status_code == 401 and refresh:
        refresh_resp = requests.post(f"{API_BASE}/auth/refresh", json={
            "refresh_token": refresh
        })

        if refresh_resp.status_code != 200:
            request.session.flush()
            return redirect("auth:login")

        new_tokens = refresh_resp.json()
        request.session["access"] = new_tokens["access_token"]
        request.session["refresh"] = new_tokens["refresh_token"]

        # Retry original request with new access token
        headers["Authorization"] = f"Bearer {new_tokens['access_token']}"
        return requests.request(method, f"{API_BASE}{path}", headers=headers, **kwargs)

    return resp
