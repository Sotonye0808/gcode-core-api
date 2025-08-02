"""
Main URL configuration for the GCode Core API.

This service handles data persistence, user management, and SVG conversion.
It provides core business logic endpoints and signed request handling.

The API provides the following main endpoints:
- /api/convert/ - SVG to G-code conversion
- /api/signed/ - Signed request endpoints (submit/retrieve)
- /api/health/ - Health check
- /admin/ - Django admin interface

For more information on URL patterns, see:
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core_api.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
