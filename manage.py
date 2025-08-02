#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This script is the main entry point for running Django management commands
for the GCode Core API service.

Usage:
    python manage.py [command] [options]

Common commands:
    python manage.py runserver        # Start the development server
    python manage.py migrate          # Apply database migrations
    python manage.py makemigrations   # Create new migrations
    python manage.py createsuperuser  # Create admin user
    python manage.py collectstatic    # Collect static files
    python manage.py test             # Run tests

For a complete list of commands, run:
    python manage.py help
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gcode_core.settings')
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
