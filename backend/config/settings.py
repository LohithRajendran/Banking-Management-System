"""
Django Settings for the Banking App
=====================================
Think of this file as the "control panel" for your entire Django project.
Everything is configured here: database, security, apps, etc.

HOW TO USE:
  - Copy .env.example to .env
  - Fill in your database password and secret key
  - Never commit your .env file to GitHub (it's in .gitignore)
"""

import os
from pathlib import Path
from decouple import config
from datetime import timedelta
try:
    import dj_database_url
except ImportError:
    dj_database_url = None


# ============================================
# BASE DIRECTORY
# ============================================
# This is the root folder of your backend project (where manage.py lives)
BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================
# SECURITY SETTINGS
# ============================================
# SECRET_KEY is used to encrypt cookies and tokens.
# NEVER share this. It's loaded from your .env file.
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production-please')

# DEBUG = True means you get detailed error pages.
# Set to False in production (live website).
DEBUG = config('DEBUG', default=True, cast=bool)

# Which domain names are allowed to access this Django app.
# '*' means anyone (fine for local development).
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')


# ============================================
# INSTALLED APPS
# ============================================
# This tells Django which features and apps to enable.
INSTALLED_APPS = [
    # --- Django Built-in Apps ---
    'django.contrib.admin',        # Admin panel at /admin/
    'django.contrib.auth',         # User authentication system
    'django.contrib.contenttypes', # Used by admin internally
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Flash messages
    'django.contrib.staticfiles',  # Static files (CSS, JS, images)

    # --- Third-Party Apps ---
    'rest_framework',              # Django REST Framework — adds API support
    'rest_framework_simplejwt',    # JWT login tokens
    'corsheaders',                 # Allows React to call Django APIs

    # --- Our Banking App ---
    'banking',
]

# Tell Django to use our custom user model (instead of the default Django user)
AUTH_USER_MODEL = 'banking.CustomUser'


# ============================================
# MIDDLEWARE
# ============================================
# Middleware runs on every request/response (like security guards).
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',      # MUST be first — handles CORS
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Serves static files efficiently in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================
# URL CONFIGURATION
# ============================================
ROOT_URLCONF = 'config.urls'


# ============================================
# TEMPLATES (for Django Admin)
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ============================================
# DATABASE
# ============================================
# By default, we use SQLite — a simple file-based database.
# No installation needed! Great for local development.
# 
# To switch to PostgreSQL:
#   1. Install PostgreSQL on your PC
#   2. Set USE_POSTGRESQL=True in your .env file
#   3. Fill in DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT in .env

DATABASE_URL = config('DATABASE_URL', default='')
USE_POSTGRESQL = config('USE_POSTGRESQL', default=False, cast=bool)

if DATABASE_URL and dj_database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif USE_POSTGRESQL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='banking_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    # SQLite — data is stored in a file called 'db.sqlite3' in your backend folder
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ============================================
# REDIS CACHE (Optional)
# ============================================
# Redis is an in-memory cache — it stores data in RAM for super-fast access.
# Used for: session data, rate limiting, frequently-read data.
#
# If Redis is not installed, Django will use a simple in-memory cache.
USE_REDIS = config('USE_REDIS', default=False, cast=bool)

if USE_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Simple in-memory cache (works without Redis, but data is lost when server restarts)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }


# ============================================
# PASSWORD VALIDATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================
# INTERNATIONALIZATION
# ============================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ============================================
# STATIC FILES
# ============================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# CORS SETTINGS
# ============================================
# CORS (Cross-Origin Resource Sharing) allows your React app (running on port 5173)
# to make API calls to your Django server (running on port 8000).
#
# In production, set CORS_ALLOWED_ORIGINS in your .env file:
#   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
# Enable CORS for production & Vercel deployments
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)

_cors_env = config('CORS_ALLOWED_ORIGINS', default='')
if _cors_env:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in _cors_env.split(',') if origin.strip()]
else:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',   # React dev server (Vite)
        'http://localhost:3000',
        'http://127.0.0.1:5173',
    ]

# Automatically allow all Vercel deployment subdomains (*.vercel.app)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]

CORS_ALLOW_CREDENTIALS = True


# ============================================
# GOOGLE SIGN-IN
# ============================================
# The OAuth 2.0 Client ID from Google Cloud Console (APIs & Services > Credentials).
# This MUST match the client ID used on the frontend (VITE_GOOGLE_CLIENT_ID) — the
# backend uses it to verify that a Google ID token was really issued for this app.
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', default='')


# ============================================
# DJANGO REST FRAMEWORK SETTINGS
# ============================================
# DRF is like an extension to Django that makes building APIs much easier.
REST_FRAMEWORK = {
    # Use JWT tokens for authentication (instead of session cookies)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # By default, only logged-in users can access APIs
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# ============================================
# JWT TOKEN SETTINGS
# ============================================
# JWT = JSON Web Token
# When a user logs in, they receive an 'access token' (short-lived, 1 day)
# and a 'refresh token' (long-lived, 7 days).
#
# The access token is sent with every API request to prove identity.
# When the access token expires, the refresh token is used to get a new one.
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),      # Access token expires in 1 day
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Refresh token expires in 7 days
    'ROTATE_REFRESH_TOKENS': True,                   # Give a new refresh token on each refresh
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),                # Token format: "Authorization: Bearer <token>"
}
