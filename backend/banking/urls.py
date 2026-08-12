"""
Banking App — URL Patterns
============================
This file maps URL paths to view functions.

HOW TO READ THIS:
  path('signup/', views.signup, ...)
  means:
  - URL:  POST http://localhost:8000/api/signup/
  - Calls: the 'signup' function in views.py

The 'name' parameter lets you reference URLs by name in code.
Example: reverse('signup') → returns '/api/signup/'
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [

    # ============================================
    # AUTHENTICATION
    # ============================================

    # POST /api/signup/ — Create a new user account
    path('signup/', views.signup, name='signup'),

    # POST /api/login/ — Login, receive JWT tokens
    path('login/', views.login, name='login'),

    # POST /api/auth/google/ — Login or signup with a Google account
    path('auth/google/', views.google_login, name='google_login'),

    # POST /api/token/refresh/ — Get a new access token using refresh token
    # (Built into Django REST Framework Simple JWT)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # ============================================
    # BANK ACCOUNT
    # ============================================

    # POST /api/create-account/ — Create bank account (must be logged in)
    path('create-account/', views.create_bank_account, name='create_bank_account'),

    # GET /api/dashboard/ — Get account info + balance + recent transactions
    path('dashboard/', views.dashboard, name='dashboard'),

    # GET /api/profile/ — Get current user's profile
    path('profile/', views.profile, name='profile'),


    # ============================================
    # TRANSFERS
    # ============================================

    # POST /api/transfer/bank/ — Transfer by account number
    path('transfer/bank/', views.bank_transfer, name='bank_transfer'),

    # POST /api/transfer/webid/ — Transfer by Web ID
    path('transfer/webid/', views.webid_transfer, name='webid_transfer'),


    # ============================================
    # TRANSACTIONS
    # ============================================

    # GET /api/transactions/ — Get transaction history
    path('transactions/', views.transaction_history, name='transaction_history'),


    # ============================================
    # LOOKUP (for verifying recipient before transfer)
    # ============================================

    # GET /api/lookup/webid/<web_id>/ — Find user by Web ID
    path('lookup/webid/<str:web_id>/', views.lookup_by_webid, name='lookup_by_webid'),

    # GET /api/lookup/account/<account_number>/ — Find account by number
    path('lookup/account/<str:account_number>/', views.lookup_by_account, name='lookup_by_account'),
]
