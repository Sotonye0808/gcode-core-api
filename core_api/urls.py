"""
URL configuration for the Core API app.

This module defines the URL patterns for core API endpoints.
It provides a RESTful API structure for SVG to G-code conversion,
user data management, and signed request handling.

API Endpoints:
- POST /api/convert/ - Convert SVG data to G-code (open access)
- GET /api/health/ - Health check endpoint (open access)

Signed Endpoints (require HMAC signature from trusted origins):
- POST /api/signed/submit/ - Submit user data and signature for storage
- POST /api/signed/retrieve/ - Retrieve user data by email

All endpoints return JSON responses and support proper HTTP status codes.
Detailed API documentation is available at each endpoint.

Example usage:
    POST /api/convert/
    Content-Type: application/json
    {
        "svg_data": "<svg>...</svg>"
    }
    
    Response:
    {
        "success": true,
        "gcode": "G28\\nG1 Z0.0\\n...",
        "message": "SVG converted successfully"
    }
"""

from django.urls import path
from . import views

app_name = 'core_api'

urlpatterns = [
    # Main conversion endpoint (open access)
    path('convert/', views.SVGToGCodeView.as_view(), name='svg_to_gcode'),
    
    # Health check endpoint (open access)
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Signed endpoints (require HMAC signature from trusted origins)
    path('signed/submit/', views.SignedSubmissionView.as_view(), name='signed_submission'),
    path('signed/retrieve/', views.UserDataRetrievalView.as_view(), name='user_data_retrieval'),
]
