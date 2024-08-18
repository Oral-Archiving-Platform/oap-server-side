from rest_framework import permissions
from apps.channel.models import ChannelMembership

'''
i do not believe we need this
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.uploaderID == request.user
'''
class IsChannelMemberOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            channel_id = request.data.get('channelID')
            if not channel_id:
                return False
            return ChannelMembership.objects.filter(
                channelID=channel_id,
                userID=request.user,
                role__in=[ChannelMembership.EDITOR, ChannelMembership.OWNER]
            ).exists()

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == "DELETE":
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