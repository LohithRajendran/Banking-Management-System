"""
config/urls.py — Django Root URL Configuration
Routes for Django Admin panel only.
FastAPI handles all /api/* routes via Nginx.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Django Admin panel — accessible at /django-admin/
    path("django-admin/", admin.site.urls),
]
