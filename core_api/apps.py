"""
Django app configuration for Core API.

This module defines the configuration for the core_api Django app.
It sets the app name and default auto field type.
"""

from django.apps import AppConfig


class CoreApiConfig(AppConfig):
    """
    Configuration class for the Core API app.
    
    This class configures the app settings including the default auto field
    type and the app name used throughout the Django project.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_api'
    verbose_name = 'Core API'
