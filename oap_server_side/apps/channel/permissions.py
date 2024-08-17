from rest_framework import permissions
from .models import ChannelMembership

class IsChannelOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action == 'create':
            channel_id = request.data.get('channelID')
            if channel_id:
                return ChannelMembership.objects.filter(
                    channelID=channel_id,
                    userID=request.user,
                    role=ChannelMembership.OWNER
                ).exists()
        
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return ChannelMembership.objects.filter(
            channelID=obj.channelID,
            userID=request.user,
            role=ChannelMembership.OWNER
        ).exists()