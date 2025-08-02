"""
Serializers for the Core API.

This module contains Django REST Framework serializers that handle
data validation and serialization for core API endpoints.

The serializers provide:
- Input validation for API requests
- Data transformation and cleaning
- Error handling for invalid data
- Documentation for API request/response formats

Classes:
    SVGToGCodeSerializer: Handles SVG data input for conversion
    UserSerializer: Handles user model serialization
    SignatureDataSerializer: Handles signature data serialization
    SignedSubmissionSerializer: Handles signed submission requests
    UserDataRetrievalSerializer: Handles user data retrieval requests
"""

from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import User, SignatureData
import base64
import io
from PIL import Image


class SVGToGCodeSerializer(serializers.Serializer):
    """
    Serializer for SVG to G-code conversion endpoint.
    
    Accepts either SVG file upload or raw SVG data string.
    Validates SVG format and content before processing.
    
    Fields:
        svg_file (FileField, optional): SVG file upload
        svg_data (CharField, optional): Raw SVG content as string
        
    Validation:
        - At least one of svg_file or svg_data must be provided
        - SVG content must be valid XML
        - File must have .svg extension if uploaded
    """
    svg_file = serializers.FileField(required=False, help_text="SVG file to convert")
    svg_data = serializers.CharField(required=False, help_text="Raw SVG content as string")
    
    def validate(self, data):
        """Validate that either svg_file or svg_data is provided."""
        if not data.get('svg_file') and not data.get('svg_data'):
            raise serializers.ValidationError(
                "Either 'svg_file' or 'svg_data' must be provided."
            )
        
        # Validate file extension if svg_file is provided
        if data.get('svg_file'):
            file = data['svg_file']
            if not file.name.lower().endswith('.svg'):
                raise serializers.ValidationError(
                    "File must have .svg extension."
                )
        
        # Basic SVG validation - only validate raw SVG data, not file uploads
        if data.get('svg_data'):
            svg_content = data['svg_data']
            if not svg_content.strip().startswith('<svg'):
                raise serializers.ValidationError(
                    "Invalid SVG content. Must start with <svg tag."
                )
        
        # For file uploads, we'll validate the content in the view after reading
        # This avoids file pointer issues during validation
            
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Handles user data validation and serialization for the playground database.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'department', 
            'faculty', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_email(self, value):
        """Validate email format."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Valid email address is required.")
        return value.lower()


class SignatureDataSerializer(serializers.ModelSerializer):
    """
    Serializer for SignatureData model.
    
    Handles signature SVG and G-code data serialization.
    """
    
    user_email = serializers.EmailField(write_only=True, required=False)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = SignatureData
        fields = [
            'id', 'user_email', 'user_name', 'svg_data', 'gcode_data',
            'gcode_metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SignedSubmissionSerializer(serializers.Serializer):
    """
    Serializer for signed submission requests from frontend.
    
    Handles user data and signature submission with signature verification.
    """
    
    # User data
    name = serializers.CharField(max_length=255, help_text="User's full name")
    email = serializers.EmailField(help_text="User's email address")
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        default='student',
        help_text="User's role"
    )
    department = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="User's department"
    )
    faculty = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="User's faculty"
    )
    submitted_at = serializers.DateTimeField(
        required=False,
        help_text="Submission timestamp"
    )
    
    # Signature data
    svg_data = serializers.CharField(help_text="SVG signature data")
    
    # Request signature for verification
    request_signature = serializers.CharField(
        help_text="HMAC signature for request verification"
    )
    
    def validate_email(self, value):
        """Validate and normalize email."""
        return value.lower().strip()
    
    def validate_svg_data(self, value):
        """Validate SVG data format."""
        if not value or not value.strip():
            raise serializers.ValidationError("SVG data cannot be empty.")
        
        if not value.strip().startswith('<svg'):
            raise serializers.ValidationError("Invalid SVG format.")
        
        return value
    
    def validate(self, data):
        """Additional validation for the entire request."""
        # Ensure required fields are present
        required_fields = ['name', 'email', 'svg_data', 'request_signature']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required.")
        
        return data


class UserDataRetrievalSerializer(serializers.Serializer):
    """
    Serializer for user data retrieval requests.
    
    Handles email-based data retrieval with signature verification.
    """
    
    email = serializers.EmailField(help_text="User's email address")
    request_signature = serializers.CharField(
        help_text="HMAC signature for request verification"
    )
    
    def validate_email(self, value):
        """Validate and normalize email."""
        return value.lower().strip()
