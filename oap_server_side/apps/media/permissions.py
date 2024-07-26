from rest_framework import permissions
from apps.channel.models import ChannelMembership

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.uploaderID == request.user

class IsChannelMemberOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method in ["DELETE"]:
            return ChannelMembership.objects.filter(
                channelID=obj.channelID,
                userID=request.user,
                role=ChannelMembership.OWNER
            ).exists()
        else:
            return ChannelMembership.objects.filter(
                channelID=obj.channelID,
                userID=request.user,
                role__in=[ChannelMembership.EDITOR, ChannelMembership.OWNER]
            ).exists()
