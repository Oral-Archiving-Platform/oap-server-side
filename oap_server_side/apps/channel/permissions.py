from rest_framework import permissions
from .models import ChannelMembership

class IsChannelOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == 'POST':
            print("just done")
            channel_id = request.data.get('channelID') or request.data.get('channel')
            if channel_id:
                return ChannelMembership.objects.filter(
                    channelID=channel_id,
                    userID=request.user,
                    role=ChannelMembership.OWNER
                ).exists()
        else:
            try:
                print('tfou')
                membership = ChannelMembership.objects.get(id=view.kwargs.get('pk'))
                channel_id = membership.channelID.id
                
                return ChannelMembership.objects.filter(
                    channelID=channel_id,
                    userID=request.user,
                    role=ChannelMembership.OWNER
                ).exists()
            except ChannelMembership.DoesNotExist:
                return False
        

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return ChannelMembership.objects.filter(
            channelID=obj.channelID,
            userID=request.user,
            role=ChannelMembership.OWNER
        ).exists()