from rest_framework import viewsets,status
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer,PlaylistDetailSerializer,AddToWatchLaterSerializer,PLaylistCreateSerializer
from apps.media.models import Media,User
from apps.media.serializers import MediaSerializer
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

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
  #new function :
    @action(detail=False, methods=['post'], url_path='create_playlists')
    def create_playlist(self, request):
        user = self.request.user
        serializer = PLaylistCreateSerializer(data=request.data)
            # Validate the data
        if serializer.is_valid():
            playlist_type = serializer.validated_data.get('type')
                
                # Prevent creation of playlists of type 'WATCHLATER'
            if playlist_type == Playlist.WATCHLATER:
                raise PermissionDenied("You already have a Watch Later playlist you cannot create one.")

                # Save the playlist, automatically setting 'created_by' to the current user
            serializer.save(created_by=user)
            return Response("sucessfully created", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
    #get the playlists of a specific userA requested by userB only public ones
    @action(detail=False, methods=['get'], url_path='user_playlists/(?P<user_id>\d+)')
    def user_playlists(self, request, user_id=None):
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
        if not User.objects.get(id=user_id):
            return Response({"error":"user id is required"}, status=401)
        # Fetch the public playlists of user B
        playlists = Playlist.objects.filter(created_by=user_b, privacy_status=Playlist.PUBLIC)
        
        # Serialize the playlists
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)
    # this is new function
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_media(self, request):
        # Get the user ID and playlist ID from the request parameters 
        user_id = request.query_params.get('user_id')  # Use query_params for GET request
        playlist_id = request.query_params.get('playlist_id')  # Use query_params for GET request
        
        # Validate IDs
        if not user_id or not playlist_id:
            return Response({"error": "Both User ID and Playlist ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_b = User.objects.get(id=user_id)
            playlist = Playlist.objects.get(id=playlist_id, created_by=user_b)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Playlist.DoesNotExist:
            return Response({"error": "Playlist not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the requester is authenticated
        user_a = request.user
        if not user_a.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check permissions to access the playlist's media
        if not (playlist.privacy_status == Playlist.PUBLIC or playlist.created_by == user_a or user_a == user_b):
            return Response({"error": "You do not have permission to access media in this playlist."}, status=status.HTTP_403_FORBIDDEN)
        # Fetch the media of the playlist
        media = PlaylistMedia.objects.filter(playlist=playlist)
        serializer = PlaylistMediaSerializer(media, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    #get by role this is a function that gets a user either : all collections or all playlists and returns them :
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_playlist_by_Role(self, request):
        user_id = request.query_params.get('user_id')
        type = request.query_params.get('type')

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        if not type:
            return Response({"error": "Playlist type is required."}, status=400)

        # Filter based on query parameters
        queryset = self.get_queryset().filter(created_by=user, privacy_status=Playlist.PUBLIC, type=type)
        serializer = self.get_serializer(queryset, many=True)
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
            raise PermissionDenied("Creation of 'Watch Later' playlist is not allowed.")
        if playlist.type == Playlist.COLLECTION:
            media = Media.objects.filter(uploaderID=user)
            if serializer.validated_data['media'] not in media:
                raise PermissionDenied("Cannot add media you do not own to a collection.")
        serializer.save(added_by=user, playlist=playlist)
    # this is in progresss
    def add_media(self, serializer):
        # Extract the media ID and playlist ID from the validated data
        media_id = serializer.validated_data.get('media_id')
        playlist_id = serializer.validated_data.get('playlist_id')

        # Fetch the media and playlist objects
        try:
            media = Media.objects.get(id=media_id)
            playlist = Playlist.objects.get(id=playlist_id)
        except Media.DoesNotExist:
            raise PermissionDenied("Media not found.")
        except Playlist.DoesNotExist:
            raise PermissionDenied("Playlist not found.")
        
        # Check if the user is the owner of the playlist
        user = self.request.user
        if playlist.created_by != user:
            raise PermissionDenied("You are not the owner of this playlist.")
        
        # Check playlist type and enforce restrictions
        if playlist.type == Playlist.COLLECTION:
            # Collection playlists can only have media owned by the user
            if media.uploaderID != user:
                raise PermissionDenied("Cannot add media you do not own to a collection.")
        elif playlist.type == Playlist.REGULAR:
            # Regular playlists can have any type of media
            pass
        else:
            raise PermissionDenied("Invalid playlist type.")        
        # Save the media with the correct 'added_by' and 'playlist' associations
        serializer.save(added_by=user, playlist=playlist)

    #rethreive all the videos uploaded by the channel    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def get_user_media(self, request, pk=None):
        # Validate the pk (user_id) parameter
        if not pk:
            return Response({"error": "User ID is required."}, status=400)

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            raise NotFound({"error": "User not found."})

        # Filter media items uploaded by the user
        media_items = Media.objects.filter(uploaderID=user)
        serializer = MediaSerializer(media_items, many=True)
        return Response(serializer.data)
    


#WATCH LATER VIEW SET: 
class WatchLaterViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path='add')
    def add_to_watch_later(self, request):
            serializer = AddToWatchLaterSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                media_id = serializer.validated_data['media_id']
                # Retrieve or create the "Watch Later" playlist
                playlist, created = Playlist.objects.get_or_create(
                    name='Watch Later',
                    created_by=user,
                    defaults={
                        'description': 'Videos to watch later',
                        'privacy_status': Playlist.PRIVATE,
                        'type': Playlist.WATCHLATER
                    }
                )

                try:
                    media = Media.objects.get(id=media_id)
                    
                    # Check if the media is already in the playlist
                    if PlaylistMedia.objects.filter(playlist=playlist, media=media).exists():
                        return Response({"message": "Video already added to Watch Later playlist"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Add media to the playlist
                    PlaylistMedia.objects.create(playlist=playlist, media=media, added_by=user)
                    
                    return Response({"message": "Video added to Watch Later playlist"}, status=status.HTTP_200_OK)
                except Media.DoesNotExist:
                    return Response({'message': 'Media not found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=False, methods=['get'], url_path='get')
    def list_watch_later(self, request):
        user = request.user
        try:
            playlist = Playlist.objects.get(name='Watch Later', created_by=user)
            playlist_media = PlaylistMedia.objects.filter(playlist=playlist)
            serializer = PlaylistMediaSerializer(playlist_media, many=True)
            return Response({"user_id": user.id, "watch_later": serializer.data}, status=status.HTTP_200_OK)
        except Playlist.DoesNotExist:
            return Response({'message': 'Watch Later playlist not found.'}, status=status.HTTP_404_NOT_FOUND)