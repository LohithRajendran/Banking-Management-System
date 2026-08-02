"""
Main URL Configuration
========================
This is the "router" of your entire Django project.
Every URL (web address) maps to a specific view (function that handles the request).

HOW IT WORKS:
  - User visits http://localhost:8000/api/login/
  - Django looks at the URL: 'api/login/'
  - It finds 'api/' → goes to banking/urls.py
  - In banking/urls.py it finds 'login/' → calls the login view
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # --- Django Admin Panel ---
    # Visit http://localhost:8000/admin/ to manage all data
    # First create a superuser: python manage.py createsuperuser
    path('admin/', admin.site.urls),

    # --- Banking API Routes ---
    # All our banking API endpoints start with /api/
    # The rest of the routing is handled in banking/urls.py
    path('api/', include('banking.urls')),
]
