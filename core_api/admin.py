"""
Django admin configuration for the Core API.

This module configures the Django admin interface for the core_api app.
It provides admin management for User and SignatureData models.

The admin interface provides:
- User management and monitoring
- Signature data viewing and management
- CSV export functionality
- Filtering and search capabilities
"""

from django.contrib import admin
from .models import User, SignatureData


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for User model.
    """
    list_display = ('name', 'email', 'role', 'department', 'faculty', 'created_at', 'updated_at')
    list_filter = ('role', 'department', 'faculty', 'created_at')
    search_fields = ('name', 'email', 'department', 'faculty')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at')
    ordering = ('-updated_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'role')
        }),
        ('Organizational Information', {
            'fields': ('department', 'faculty')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        """Export selected users as CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Role', 'Department', 'Faculty', 'Created At'])
        
        for user in queryset:
            writer.writerow([
                user.name, user.email, user.role, 
                user.department, user.faculty, user.created_at
            ])
        
        return response
    
    export_as_csv.short_description = "Export selected users as CSV"


@admin.register(SignatureData)
class SignatureDataAdmin(admin.ModelAdmin):
    """
    Admin interface for SignatureData model.
    """
    list_display = ('user', 'created_at', 'gcode_lines', 'gcode_size')
    list_filter = ('created_at',)
    search_fields = ('user__name', 'user__email')
    readonly_fields = ('created_at', 'gcode_lines', 'gcode_size')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Signature Data', {
            'fields': ('svg_data',)
        }),
        ('Generated G-code', {
            'fields': ('gcode_data', 'gcode_metadata'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('gcode_lines', 'gcode_size', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def gcode_lines(self, obj):
        """Get G-code line count from metadata."""
        return obj.gcode_metadata.get('gcode_lines', 0)
    
    def gcode_size(self, obj):
        """Get G-code size from metadata."""
        return f"{obj.gcode_metadata.get('gcode_size', 0)} bytes"
    
    gcode_lines.short_description = 'G-code Lines'
    gcode_size.short_description = 'G-code Size'
