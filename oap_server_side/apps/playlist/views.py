from rest_framework import viewsets
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer,PlaylistDetailSerializer
from apps.media.models import Media
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes=[IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Playlist.objects.filter(
                Q(privacy_status=Playlist.PUBLIC) |
                Q(created_by=user)
            )
        return Playlist.objects.filter(privacy_status=Playlist.PUBLIC)
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaylistDetailSerializer  # Use detailed serializer for retrieve action taht shows teh associate playlistmedia
        return PlaylistSerializer
    #users cannot see a playlist if it is private and they are not the owner
    #users can only delete a playlist if they are the owner same for update etc
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        obj = serializer.instance
        if obj.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to edit this playlist.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this playlist.")
        instance.delete()



class PlaylistMediaViewSet(viewsets.ModelViewSet):
    queryset = PlaylistMedia.objects.all()
    serializer_class = PlaylistMediaSerializer
    #users can only add media to their own playlists and you can only add media you own to a collection
    #both playlists and collections can be public or private
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return PlaylistMedia.objects.filter(
                Q(playlist__privacy_status=Playlist.PUBLIC) |
                Q(playlist__created_by=user)
            ).prefetch_related('media__video_media')
        return PlaylistMedia.objects.filter(playlist__privacy_status=Playlist.PUBLIC).prefetch_related('media__video_media')
    def perform_create(self, serializer):
        playlist = serializer.validated_data.get('playlist')
        user = self.request.user
        if playlist.created_by != user:
            raise PermissionDenied("You are not the owner of this playlist.")
        
        if playlist.type == Playlist.COLLECTION:
            media = Media.objects.filter(uploaderID=user)
            if serializer.validated_data['media'] not in media:
                raise PermissionDenied("Cannot add media you do not own to a collection.")
        serializer.save(added_by=user, playlist=playlist)
    
