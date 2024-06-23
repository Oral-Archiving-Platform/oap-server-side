from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer
from apps.media.models import Media
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.users.models import User
from rest_framework.exceptions import PermissionDenied


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    """@action(detail=False, methods=['get'], url_path='user-collections')
    def user_collections(self, request):
        user = request.user
        playlists = self.queryset.filter(uploaderID=user, type=Playlist.COLLECTION)
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='user-playlists')
    def user_playlists(self, request):
        user = request.user
        playlists = self.queryset.filter(uploaderID=user, type=Playlist.PLAYLIST)
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)"""

class PlaylistMediaViewSet(viewsets.ModelViewSet):
    queryset = PlaylistMedia.objects.all()
    serializer_class = PlaylistMediaSerializer

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
    
