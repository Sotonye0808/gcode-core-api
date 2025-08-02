"""
Tests for the Core API.

This module contains test cases for the core_api app functionality.
Tests cover models, views, services, and API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, SignatureData
from .services import SVGConversionService, UserDataService


class UserModelTest(TestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test creating a new user."""
        user = User.objects.create(
            name="Test User",
            email="test@example.com",
            role="student",
            department="Computer Science"
        )
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "student")
        self.assertEqual(str(user), "Test User (test@example.com)")


class SignatureDataModelTest(TestCase):
    """Test cases for SignatureData model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create(
            name="Test User",
            email="test@example.com"
        )
    
    def test_signature_creation(self):
        """Test creating signature data."""
        signature = SignatureData.objects.create(
            user=self.user,
            svg_data="<svg></svg>",
            gcode_data="G28\nG1 X0 Y0",
            gcode_metadata={"lines": 2}
        )
        self.assertEqual(signature.user, self.user)
        self.assertEqual(signature.svg_data, "<svg></svg>")


class SVGToGCodeAPITest(APITestCase):
    """Test cases for SVG to G-code conversion API."""
    
    def test_convert_svg_success(self):
        """Test successful SVG conversion."""
        url = reverse('core_api:svg_to_gcode')
        data = {
            'svg_data': '<svg width="100" height="100"><rect x="10" y="10" width="80" height="80"/></svg>'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success']) # type: ignore
        self.assertIn('gcode', response.data) # type: ignore
    
    def test_convert_svg_no_data(self):
        """Test conversion with no SVG data."""
        url = reverse('core_api:svg_to_gcode')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success']) # type: ignore


class HealthCheckAPITest(APITestCase):
    """Test cases for health check API."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        url = reverse('core_api:health_check')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy') # type: ignore
        self.assertEqual(response.data['service'], 'GCode Core API') # type: ignore
        self.assertIn('endpoints', response.data) # type: ignore
