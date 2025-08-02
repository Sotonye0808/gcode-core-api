"""
Django models for the Core API.

This module contains Django model definitions for the core_api app.
These models handle user data and signature information for the playground database.

Models:
    User: Basic user information for testing and data collection
    SignatureData: SVG and G-code data associated with users
"""

from django.db import models
from django.utils import timezone
import json


class User(models.Model):
    """
    User model for playground database.
    
    This model stores basic user information for testing and data collection.
    Users are identified by email address and can be updated if they exist.
    """
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('hod', 'Head of Department'),
        ('dean', 'Dean'),
        ('researcher', 'Researcher'),
        ('visitor', 'Visitor'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255, help_text="Full name of the user")
    email = models.EmailField(unique=True, help_text="Email address (unique identifier)")
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='student',
        help_text="User's role in the organization"
    )
    department = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Department or division"
    )
    faculty = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Faculty or school"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the user first submitted data"
    )
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class SignatureData(models.Model):
    """
    Signature data model for storing SVG and G-code information.
    
    This model stores the signature SVG data and corresponding G-code
    for each user submission.
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='signatures',
        help_text="User who submitted this signature"
    )
    svg_data = models.TextField(help_text="Raw SVG data")
    gcode_data = models.TextField(help_text="Generated G-code")
    gcode_metadata = models.JSONField(
        default=dict,
        help_text="Metadata about the G-code (lines, size, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signature Data"
        verbose_name_plural = "Signature Data"
    
    def __str__(self):
        return f"Signature for {self.user.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
