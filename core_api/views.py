"""
API views for the Core API.

This module contains Django REST Framework views that handle HTTP requests
for SVG to G-code conversion, user data management, and signed requests.

The views provide:
- RESTful API endpoints with proper HTTP methods
- Comprehensive error handling and validation
- Detailed API documentation
- Consistent JSON response formats
- Request/response logging

Classes:
    SVGToGCodeView: Handles SVG to G-code conversion requests
    HealthCheckView: Provides API health status
    SignedSubmissionView: Handles signed user data submission
    UserDataRetrievalView: Handles signed user data retrieval
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import JsonResponse

from .serializers import (
    SVGToGCodeSerializer,
    SignedSubmissionSerializer,
    UserDataRetrievalSerializer,
    UserSerializer,
    SignatureDataSerializer
)
from .services import (
    SVGConversionService, 
    SignatureVerificationService,
    UserDataService
)

logger = logging.getLogger(__name__)


class SVGToGCodeView(APIView):
    """
    API endpoint for converting SVG data to G-code.
    
    This endpoint accepts SVG data either as a file upload or raw SVG string
    and returns the corresponding G-code for CNC machines or 3D printers.
    
    **POST /api/convert/**
    
    Request formats:
    1. File upload (multipart/form-data):
       - svg_file: SVG file upload
       
    2. JSON data (application/json):
       - svg_data: Raw SVG content as string
    
    Response format:
    ```json
    {
        "success": true,
        "gcode": "G28\\nG1 Z0.0\\nM05\\n...",
        "message": "SVG converted successfully to G-code",
        "metadata": {
            "gcode_lines": 150,
            "gcode_size": 2048,
            "movement_commands": 120,
            "setup_commands": 30,
            "estimated_duration": "15.0 seconds"
        }
    }
    ```
    
    Error responses:
    ```json
    {
        "success": false,
        "error": "Error type",
        "details": "Detailed error information"
    }
    ```
    
    **Status Codes:**
    - 200: Conversion successful
    - 400: Bad request (invalid SVG data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for SVG to G-code conversion."""
        try:
            # Validate request data
            serializer = SVGToGCodeSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"SVG conversion validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Extract SVG content
            if 'svg_file' in validated_data: # type: ignore
                svg_file = validated_data['svg_file'] # type: ignore
                logger.info(f"Processing SVG file: {svg_file.name} ({svg_file.size} bytes)")
                
                try:
                    svg_content = svg_file.read().decode('utf-8')
                    svg_file.seek(0)  # Reset file pointer
                    
                    # Validate SVG content starts with <svg
                    if not svg_content.strip().startswith('<svg'):
                        raise ValueError("Invalid SVG file content. Must start with <svg tag.")
                        
                except UnicodeDecodeError:
                    logger.error("SVG file encoding error")
                    return Response({
                        'success': False,
                        'error': 'Invalid file encoding',
                        'details': 'SVG file must be UTF-8 encoded'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                svg_content = validated_data['svg_data'] # type: ignore
                logger.info("Processing SVG data from request body")
            
            # Additional SVG content validation
            if not svg_content or len(svg_content.strip()) == 0:
                raise ValueError("SVG content is empty")
            
            # Convert SVG to G-code
            gcode = SVGConversionService.convert_svg_to_gcode(svg_content)
            
            # Calculate metadata - FIXED LINE COUNTING
            # Split by actual newlines and filter out empty lines
            gcode_lines_list = [line.strip() for line in gcode.split('\n') if line.strip()]
            gcode_lines = len(gcode_lines_list)
            gcode_size = len(gcode.encode('utf-8'))
            
            # Count specific G-code command types for additional metadata
            movement_commands = len([line for line in gcode_lines_list if line.startswith(('G0', 'G1', 'G2', 'G3'))])
            setup_commands = len([line for line in gcode_lines_list if line.startswith(('G28', 'G90', 'G91', 'M'))])
            
            logger.info(f"SVG conversion successful: {gcode_lines} lines ({movement_commands} movements, {setup_commands} setup), {gcode_size} bytes")
           
            return Response({
                'success': True,
                'gcode': gcode,
                'message': 'SVG converted successfully to G-code',
                'metadata': {
                    'gcode_lines': gcode_lines,
                    'gcode_size': gcode_size,
                    'movement_commands': movement_commands,
                    'setup_commands': setup_commands,
                    'estimated_duration': f"{gcode_lines * 0.1:.1f} seconds"  # Rough estimate
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"SVG conversion validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid SVG data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"SVG conversion server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during conversion'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    API endpoint for health check and service information.
    
    **GET /api/health/**
    
    Returns the current status of the API service along with available endpoints
    and version information.
    
    Response format:
    ```json
    {
        "status": "healthy",
        "service": "GCode Core API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T12:00:00Z",
        "endpoints": {
            "convert": "/api/convert/",
            "signed_submit": "/api/signed/submit/",
            "signed_retrieve": "/api/signed/retrieve/"
        }
    }
    ```
    """
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for health check."""
        from django.utils import timezone
        
        return Response({
            'status': 'healthy',
            'service': 'GCode Core API',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat(),
            'endpoints': {
                'convert': '/api/convert/',
                'signed_submit': '/api/signed/submit/',
                'signed_retrieve': '/api/signed/retrieve/'
            }
        }, status=status.HTTP_200_OK)


class SignedSubmissionView(APIView):
    """
    API endpoint for submitting user data and signatures (signed requests only).
    
    This endpoint accepts user information and SVG signature data from trusted
    frontend origins with proper HMAC signature verification.
    
    **POST /api/signed/submit/**
    
    Headers required:
    - Origin: Must be from trusted frontend origin
    - Content-Type: application/json
    
    Request format:
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com",
        "role": "student",
        "department": "Computer Science",
        "faculty": "Engineering",
        "svg_data": "<svg>...</svg>",
        "request_signature": "hmac_signature_here"
    }
    ```
    
    Response format:
    ```json
    {
        "success": true,
        "message": "Data submitted successfully",
        "user_id": 123,
        "signature_id": 456,
        "gcode": "G28\\nG1 Z0.0\\n...",
        "metadata": {
            "gcode_lines": 150,
            "gcode_size": 2048
        }
    }
    ```
    """
    
    parser_classes = [JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle signed user data submission from trusted frontend."""
        try:
            # Get request origin
            origin = request.META.get('HTTP_ORIGIN', '')
            
            # Validate request data
            serializer = SignedSubmissionSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Signed submission validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Verify request signature
            signature = validated_data.get('request_signature') # type: ignore
            if not SignatureVerificationService.verify_request_signature(
                validated_data, signature, origin # type: ignore
            ):
                logger.warning(f"Invalid signature for signed submission from origin: {origin}")
                return Response({
                    'success': False,
                    'error': 'Invalid signature',
                    'details': 'Request signature verification failed'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Create or update user
            user = UserDataService.create_or_update_user(validated_data) # type: ignore
            
            # Store signature data
            signature_data = UserDataService.store_signature_data(
                user, validated_data['svg_data'] # type: ignore
            )
            
            logger.info(f"Signed submission successful for user: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Data submitted successfully',
                'user_id': user.id, # type: ignore
                'signature_id': signature_data.id, # type: ignore
                'gcode': signature_data.gcode_data,
                'metadata': signature_data.gcode_metadata
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Signed submission data error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Data processing error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Signed submission server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred while processing submission'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDataRetrievalView(APIView):
    """
    API endpoint for retrieving user data by email (signed requests only).
    
    This endpoint retrieves all stored user data and signatures for a given
    email address from trusted frontend origins with proper HMAC signature verification.
    
    **POST /api/signed/retrieve/**
    
    Headers required:
    - Origin: Must be from trusted frontend origin
    - Content-Type: application/json
    
    Request format:
    ```json
    {
        "email": "john@example.com",
        "request_signature": "hmac_signature_here"
    }
    ```
    
    Response format:
    ```json
    {
        "success": true,
        "user": {
            "id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "role": "student",
            "department": "Computer Science",
            "faculty": "Engineering",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "submitted_at": "2024-01-01T12:00:00Z"
        },
        "signatures": [
            {
                "id": 456,
                "svg_data": "<svg>...</svg>",
                "gcode_data": "G28\\nG1...",
                "metadata": {...},
                "created_at": "2024-01-01T12:00:00Z"
            }
        ]
    }
    ```
    """
    
    parser_classes = [JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle user data retrieval from trusted frontend."""
        try:
            # Get request origin
            origin = request.META.get('HTTP_ORIGIN', '')
            
            # Validate request data
            serializer = UserDataRetrievalSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Data retrieval validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Verify request signature
            signature = validated_data.get('request_signature') # type: ignore
            if not SignatureVerificationService.verify_request_signature(
                validated_data, signature, origin # type: ignore
            ):
                logger.warning(f"Invalid signature for data retrieval from origin: {origin}")
                return Response({
                    'success': False,
                    'error': 'Invalid signature',
                    'details': 'Request signature verification failed'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Retrieve user data
            user_data = UserDataService.get_user_data(validated_data['email']) # type: ignore
            
            if user_data is None:
                return Response({
                    'success': False,
                    'error': 'User not found',
                    'details': f"No user found with email: {validated_data['email']}" # type: ignore
                }, status=status.HTTP_404_NOT_FOUND)
            
            logger.info(f"Data retrieval successful for user: {validated_data['email']}") # type: ignore
            
            return Response({
                'success': True,
                **user_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Data retrieval validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Data processing error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Data retrieval server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred while retrieving data'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
