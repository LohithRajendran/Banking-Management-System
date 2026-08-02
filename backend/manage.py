#!/usr/bin/env python
"""
manage.py — Django's Command-Line Utility
==========================================
You use this file to run Django commands from your terminal.

COMMON COMMANDS:
  python manage.py runserver          → Start the development server
  python manage.py makemigrations     → Create database migration files (after changing models)
  python manage.py migrate            → Apply migrations to the database
  python manage.py createsuperuser    → Create an admin user for the admin panel
  python manage.py shell              → Open a Python shell with Django loaded
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
