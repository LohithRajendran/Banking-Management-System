"""
WSGI stands for "Web Server Gateway Interface".
This file is used when deploying Django to a production server (like Railway or Render).
For local development, you use 'python manage.py runserver' instead.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
