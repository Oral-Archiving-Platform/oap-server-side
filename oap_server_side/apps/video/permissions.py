from rest_framework import permissions
from apps.channel.models import ChannelMembership
import json
#i dont believe e need this anymore because all videos belong to a channel
""""class IsVideoOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.mediaID.uploaderID == request.user"""
    
class IsChannelMemberOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For create operations
        if request.method == 'POST':
            print(request.data)
            video_data = json.loads(request.data.get('video', '{}'))
            channel_id = video_data.get('mediaID', {}).get('channelID')
            print("POST permission",channel_id)
            if not channel_id:
                print("POST permissio no channel")
                return False  # Reject if channelID is not provided
            return self.check_channel_membership(request.user, channel_id)
        
        return True  # Let has_object_permission handle other cases

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            print("safe meth object permission")
            return True
        video_data = json.loads(request.data.get('video', '{}'))
        channel_id = video_data.get('mediaID', {}).get('channelID')
        return self.check_channel_membership(request.user, channel_id, require_owner=request.method == 'DELETE')

    def check_channel_membership(self, user, channel_id, require_owner=False):
        print("check channel membership",channel_id)

        roles = [ChannelMembership.OWNER] if require_owner else [ChannelMembership.EDITOR, ChannelMembership.OWNER]
        val=ChannelMembership.objects.filter(
            channelID_id=channel_id,
            userID=user,
            role__in=roles
        ).exists()
        print("val",val)
        return val