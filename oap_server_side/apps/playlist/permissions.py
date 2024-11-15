from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    # Custom permission to only allow owners of an object to edit it= permissions for specific object
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user

