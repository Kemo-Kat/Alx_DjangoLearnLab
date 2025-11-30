"""
Custom permissions for the API application.

This module defines custom permission classes for fine-grained access control
beyond Django REST Framework's built-in permissions.
"""

from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users,
    but require authentication for write operations.
    
    This is similar to DRF's built-in IsAuthenticatedOrReadOnly,
    but demonstrates how to create custom permission logic.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed to any request.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        # Note: This assumes the object has an 'owner' field
        # For our Book model, we might use 'author' or add an 'owner' field
        return obj.owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read permissions are allowed to any request.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require admin user
        return request.user and request.user.is_staff