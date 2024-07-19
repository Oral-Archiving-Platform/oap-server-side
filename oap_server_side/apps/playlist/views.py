from rest_framework import viewsets
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer,PlaylistDetailSerializer
from apps.media.models import Media,User
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
#independetly fetch 
#one endpoint
#to add a function gets 3 differnet endpoints for the types
#collections: innput user id, base on user id 
#already implement for get videos 
#rethreive all teh videos of a channel

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
        user = self.request.user
        playlist_type = serializer.validated_data.get('type')
        #cannot create playlists of type watchlater
        if playlist_type == Playlist.WATCHLATER :
            raise PermissionDenied("You already have a Watch Later playlist.")
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        obj = serializer.instance
        if obj.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to edit this playlist.")
        serializer.save()
    def perform_destroy(self, instance):
        if instance.created_by != self.request.user:
            raise PermissionDenied("You do not have permission to delete this playlist.")
        #assuming that watch later playlist cannot deleted
        if instance.type == Playlist.WATCHLATER:
            raise PermissionDenied("You cannot delete a Watch Later playlist.")
        instance.delete()

    #get the playlists of a specific userA requested by userB

    @action(detail=False, methods=['get'])
    def user_playlists(self, request):
        # Get the user ID from the request data
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        try:
            user_b = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        # Check if the requester is authenticated
        user_a = self.request.user
        if not user_a.is_authenticated:
            return Response({"error": "Authentication required."}, status=401)
        # Fetch the private playlists of user B
        playlists = Playlist.objects.filter(created_by=user_b, privacy_status=Playlist.PUBLIC)
        # Serialize the playlists
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)
    # types : collection : cannot add videos that are not urs
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_media(self, request):
        # Get the user ID and playlist ID from the request parameters 
        user_id = request.data.get('user_id')
        playlist_id = request.data.get('playlist_id')
        
        # Validate IDs
        if not user_id or not playlist_id:
            return Response({"error": "Both User ID and Playlist ID are required."}, status=400)
        
        try:
            user_b = User.objects.get(id=user_id)

            playlist = Playlist.objects.get(id=playlist_id,created_by=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=404)
        # Check if the requester is authenticated
        user_a = self.request.user
        if not user_a.is_authenticated:
            return Response({"error": "Authentication required."}, status=401)
        # Check permissions to access the playlist's media
        if not (playlist.privacy_status == Playlist.PUBLIC or playlist.created_by == user_a or user_a == user_b):
            return Response({"error": "You do not have permission to access media in this playlist."}, status=403)
        # Fetch the media of the playlist
        media = PlaylistMedia.objects.filter(playlist=playlist)
        serializer = PlaylistMediaSerializer(media, many=True)
        return Response(serializer.data)
    #get by role this is a function that gets a user either : all collections or all playlists and returns them :
    @action(detail=False, methods=['get'])
    def get_by_Role(self, request):
        # Get the user ID from the request data
        user_id = request.data.get('user_id')
        type = request.data.get('type')
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        if not type:
            return Response({"error": "playlist type is required"}, status=404)
        # Check if the requester is authenticated
        # Fetch the private playlists of user B
        playlists = Playlist.objects.filter(created_by=user,privacy_status=Playlist.PUBLIC,type =type )
        # Serialize the playlists
        serializer = self.get_serializer(playlists, many=True)
        return Response(serializer.data)
    
        
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
        #if watch later exists add the media to it, otherwise create it 
        if playlist.type == Playlist.WATCHLATER:
            watch_later_playlist = Playlist.objects.filter(created_by=user, type=Playlist.WATCHLATER).first()
            if not watch_later_playlist:
                watch_later_playlist = Playlist.objects.create(
                    name="Watch Later",
                    description="Automatically created Watch Later playlist",
                    type=Playlist.WATCHLATER,
                    privacy_status=Playlist.PRIVATE,  # Example privacy status, adjust as needed
                    created_by=user
                )
        if playlist.type == Playlist.COLLECTION:
            media = Media.objects.filter(uploaderID=user)
            if serializer.validated_data['media'] not in media:
                raise PermissionDenied("Cannot add media you do not own to a collection.")
        serializer.save(added_by=user, playlist=playlist)
    #rethreive all the videos of a channel    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_channel_videos(self, request):
        # types : collection : cannot add videos that are not urs
        user_id = request.data.get('user_id')
        # Validate IDs
        if not user_id:
            return Response({"error": " User ID required"}, status=400)
        try:
            user= User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        Playlists= Playlist.objects.filter(created_by=user, status=Playlist.PUBLIC).prefetch_related('media__video_media')
        all_media =[]
        for playlist in Playlists :
            media = PlaylistMedia.objects.filter(playlist=playlist)
            all_media.extend(media)
        serializer = PlaylistMediaSerializer(all_media, many=True)
        return Response(serializer.data)



    
