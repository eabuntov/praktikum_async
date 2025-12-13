# django_app/auth/views.py
import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages

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
            return redirect("login")

        data = resp.json()

        # Save tokens to session
        request.session["access"] = data["access_token"]
        request.session["refresh"] = data["refresh_token"]

        return redirect("dashboard")

    return render(request, "login.html")
