from rest_framework import permissions
from .models import User

class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  
        return request.user.is_authenticated and request.user.role == request.user.ADMIN  # Only admins can edit or create