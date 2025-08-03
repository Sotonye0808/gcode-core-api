"""
Service layer for Core API business logic.

This module contains the core business logic for SVG to G-code conversion,
user data management, and signature verification. It acts as an interface 
between the API views and the underlying conversion/data storage modules.

The service layer provides:
- SVG to G-code conversion functionality
- User data management
- Signature verification for trusted requests
- File handling and temporary file management
- Error handling and logging

Classes:
    SVGConversionService: Handles SVG to G-code conversion
    SignatureVerificationService: Handles HMAC signature verification
    UserDataService: Handles user data management
"""

import os
import tempfile
import logging
from typing import Tuple, Optional, List, Union, Dict, Any
import hmac
import hashlib
import json
from datetime import datetime
from django.conf import settings
from django.utils import timezone

# Import our existing modules
from py_svg2gcode import SVGConverter
from .models import User, SignatureData

logger = logging.getLogger(__name__)


class SVGConversionService:
    """
    Service class for handling SVG to G-code conversion.
    
    This service provides a clean interface for converting SVG data
    to G-code using the existing py_svg2gcode module.
    """
    
    @staticmethod
    def convert_svg_to_gcode(svg_content: str) -> str:
        """
        Convert SVG content to G-code.
        
        Args:
            svg_content (str): The SVG content as a string
            
        Returns:
            str: Generated G-code content
            
        Raises:
            ValueError: If SVG content is invalid
            RuntimeError: If conversion fails
        """
        try:
            # Create a temporary file for the SVG content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_file:
                temp_file.write(svg_content)
                temp_svg_path = temp_file.name
            
            try:
                # Create converter and generate G-code
                converter = SVGConverter(debugging=False, toDefDir=False)
                gcode = converter.generate_gcode(temp_svg_path)
                
                if not gcode or not gcode.strip():
                    raise ValueError("Generated G-code is empty")
                
                logger.info(f"Successfully converted SVG to G-code ({len(gcode)} characters)")
                return gcode
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_svg_path):
                    os.unlink(temp_svg_path)
                    
        except Exception as e:
            logger.error(f"Error converting SVG to G-code: {str(e)}")
            raise RuntimeError(f"SVG conversion failed: {str(e)}")


class SignatureVerificationService:
    """
    Service for verifying signed requests from trusted frontend origins.
    
    This service handles HMAC signature verification to ensure requests
    are coming from authorized frontend applications.
    """
    
    @staticmethod
    def get_trusted_origins():
        """Get list of trusted frontend origins."""
        return getattr(settings, 'TRUSTED_FRONTEND_ORIGINS', [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:4200',
            'http://127.0.0.1:4200',
        ])
    
    @staticmethod
    def get_signing_key():
        """Get the signing key for HMAC verification."""
        key = getattr(settings, 'FRONTEND_SIGNING_KEY', 'dev-signing-key-change-in-production')
        # Strip any extra quotes or whitespace
        return key.strip().strip('"').strip("'")
    
    @staticmethod
    def verify_request_signature(data: Dict[str, Any], signature: str, origin: str) -> bool:
        """
        Verify HMAC signature for a request.
        
        Args:
            data: Request data to verify
            signature: HMAC signature to verify
            origin: Request origin
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Check if origin is trusted
            trusted_origins = SignatureVerificationService.get_trusted_origins()
            
            if origin not in trusted_origins:
                logger.warning(f"Request from untrusted origin: {origin}")
                return False
            
            # Create canonical string from data
            canonical_data = SignatureVerificationService._create_canonical_string(data)
            
            # Calculate expected signature
            signing_key = SignatureVerificationService.get_signing_key()
            
            expected_signature = hmac.new(
                signing_key.encode('utf-8'),
                canonical_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            """ logger.info(f"Expected signature: {expected_signature}")
            logger.info(f"Received signature: {signature}")
            logger.info(f"Signature lengths - Expected: {len(expected_signature)}, Received: {len(signature)}") """
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                logger.warning(f"Invalid signature from origin: {origin}")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"Error verifying request signature: {str(e)}")
            return False
    
    @staticmethod
    def _create_canonical_string(data: Dict[str, Any]) -> str:
        """
        Create canonical string representation of data for signing.
        
        Args:
            data: Dictionary of data to canonicalize
            
        Returns:
            str: Canonical string representation
        """
        # Remove signature field from data
        clean_data = {k: v for k, v in data.items() if k != 'request_signature'}
        
        # Sort keys and create canonical string
        sorted_items = sorted(clean_data.items())
        canonical_parts = []
        
        for key, value in sorted_items:
            if isinstance(value, dict):
                value = json.dumps(value, sort_keys=True)
            elif isinstance(value, list):
                value = json.dumps(value, sort_keys=True)
            elif value is None:
                value = ''
            else:
                value = str(value)
        
            part = f"{key}={value}"
            canonical_parts.append(part)
        
        canonical_string = "&".join(canonical_parts)
        return canonical_string


class UserDataService:
    """
    Service for managing user data in the playground database.
    
    This service handles user creation, updates, and data retrieval
    for the testing and data collection phase.
    """
    
    @staticmethod
    def create_or_update_user(user_data: Dict[str, Any]) -> User:
        """
        Create a new user or update existing user based on email.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            User: Created or updated user instance
        """
        try:
            email = user_data['email'].lower()
            
            # Try to get existing user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'name': user_data['name'],
                    'role': user_data.get('role', 'student'),
                    'department': user_data.get('department', ''),
                    'faculty': user_data.get('faculty', ''),
                    'submitted_at': user_data.get('submitted_at', timezone.now())
                }
            )
            
            # Update existing user if not created
            if not created:
                user.name = user_data['name']
                user.role = user_data.get('role', user.role)
                user.department = user_data.get('department', user.department)
                user.faculty = user_data.get('faculty', user.faculty)
                # Don't update submitted_at for existing users
                user.save()
                
                logger.info(f"Updated existing user: {email}")
            else:
                logger.info(f"Created new user: {email}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error creating/updating user: {str(e)}")
            raise ValueError(f"Failed to create/update user: {str(e)}")
    
    @staticmethod
    def store_signature_data(user: User, svg_data: str) -> SignatureData:
        """
        Store signature data and generate g-code for a user with a maximum of 2 signatures.
        If user already has 2 signatures, delete the oldest one.
        
        Args:
            user: User instance
            svg_data: SVG content
            
        Returns:
            SignatureData: Created signature data instance
        """
        try:
            # Generate G-code from SVG
            gcode = SVGConversionService.convert_svg_to_gcode(svg_data)
            
            # Calculate metadata
            gcode_lines_list = [line.strip() for line in gcode.split('\n') if line.strip()]
            gcode_lines = len(gcode_lines_list)
            gcode_size = len(gcode.encode('utf-8'))
            
            movement_commands = len([line for line in gcode_lines_list if line.startswith(('G0', 'G1', 'G2', 'G3'))])
            setup_commands = len([line for line in gcode_lines_list if line.startswith(('G28', 'G90', 'G91', 'M'))])
            
            metadata = {
                'gcode_lines': gcode_lines,
                'gcode_size': gcode_size,
                'movement_commands': movement_commands,
                'setup_commands': setup_commands,
                'estimated_duration': f"{gcode_lines * 0.1:.1f} seconds"
            }
            
           # Check existing signature count
            existing_signatures = SignatureData.objects.filter(user=user).order_by('created_at')
            
            # If user has 2 or more signatures, delete the oldest ones to maintain limit of 2
            if existing_signatures.count() >= 2:
                # Get the most recent signature to keep
                most_recent = existing_signatures.last()
                
                # Delete all signatures except the most recent one
                SignatureData.objects.filter(user=user).exclude(id=most_recent.id).delete()
            
            # Create new signature

            signature_data = SignatureData.objects.create(
                user=user,
                svg_data=svg_data,
                gcode_data=gcode,
                gcode_metadata=metadata
            )
            
            logger.info(f"Stored signature data for user: {user.email}")
            return signature_data
            
        except Exception as e:
            logger.error(f"Error storing signature data: {str(e)}")
            raise ValueError(f"Failed to store signature data: {str(e)}")
    
    @staticmethod
    def get_user_data(email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve all data for a user by email.
        
        Args:
            email: User's email address
            
        Returns:
            dict: User data with signatures, or None if not found
        """
        try:
            email = email.lower()
            user = User.objects.get(email=email)
            
            # Get all signatures for the user
            signatures = SignatureData.objects.filter(user=user).order_by('-created_at')
            
            user_data = {
                'user': {
                    'id': user.id, # type: ignore
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'department': user.department,
                    'faculty': user.faculty,
                    'created_at': user.created_at.isoformat(),
                    'updated_at': user.updated_at.isoformat(),
                    'submitted_at': user.submitted_at.isoformat()
                },
                'signatures': []
            }
            
            for signature in signatures:
                signature_info = {
                    'id': signature.id, # type: ignore
                    'svg_data': signature.svg_data,
                    'gcode_data': signature.gcode_data,
                    'metadata': signature.gcode_metadata,
                    'created_at': signature.created_at.isoformat()
                }
                user_data['signatures'].append(signature_info)
            
            logger.info(f"Retrieved data for user: {email}")
            return user_data
            
        except User.DoesNotExist:
            logger.info(f"User not found: {email}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user data: {str(e)}")
            raise ValueError(f"Failed to retrieve user data: {str(e)}")
