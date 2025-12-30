import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages

from fastapi_auth.models import RemoteUser

API_BASE = settings.AUTH_API_URL

def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        resp = requests.post(f"{API_BASE}/auth/login", json={
            "email": email,
            "password": password
        })

        if resp.status_code != 200:
            messages.error(request, "Invalid credentials")
            return redirect("auth:login")

        data = resp.json()

        # Save tokens to session
        request.session["access"] = data["access_token"]
        request.session["refresh"] = data["refresh_token"]

        user_data = data["user"]

        RemoteUser.objects.update_or_create(
            id=user_data["id"],
            defaults=user_data
        )

        return redirect("/admin")
    return render(request, "fastapi_auth/login.html")


def logout_view(request):
    refresh = request.session.get("refresh")

    if refresh:
        requests.post(f"{API_BASE}/auth/logout", json={
            "refresh_token": refresh
        })

    request.session.flush()
    return redirect("auth:login")
