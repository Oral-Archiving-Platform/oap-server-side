from rest_framework import viewsets,status
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer,PlaylistDetailSerializer,AddToWatchLaterSerializer
from apps.media.models import Media,User
from apps.media.serializers import MediaSerializer
from rest_framework.exceptions import PermissionDenied
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from apps.channel.models import ChannelMembership
from django.shortcuts import get_object_or_404
from apps.channel.models import Channel


#independetly fetch 
#one endpoint
#to add a function gets 3 differnet endpoints for the types
#collections: innput user id, base on user id 
#already implement for get videos 
#rethrive all the videos of a channel

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
            return PlaylistDetailSerializer  # Use detailed serializer for retrieve action that shows the associate playlistmedia
        return PlaylistSerializer
    #users cannot see a playlist if it is private and they are not the owner
    #users can only delete a playlist if they are the owner same for update etc   

    def perform_create(self, serializer):

        user = self.request.user
        playlist_type = serializer.validated_data.get('type')
        channel = serializer.validated_data.get('channel')
        if not channel:
            raise PermissionDenied("Collections must be associated with a channel.")

        # Check if the user is the owner or editor of the channel before being able to create a collection for it
        if playlist_type == Playlist.COLLECTION:
            is_channel_owner = ChannelMembership.objects.filter(
                userID=self.request.user,
                channelID=channel,
                role__in=[ChannelMembership.EDITOR, ChannelMembership.OWNER]
            ).exists()
            
            if not is_channel_owner:
                raise PermissionDenied("You do not have permission to create collections for this channel.")

        #cannot create playlists of type watchlater
        if playlist_type == Playlist.WATCHLATER :
            raise PermissionDenied("You already have a Watch Later playlist.")
        
        serializer.save(created_by=user)

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
        
        # Fetch the public playlists of user B
        playlists = Playlist.objects.filter(created_by=user_b, privacy_status=Playlist.PUBLIC)
        
        # Serialize the playlists
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)
    # types : collection : cannot add videos that are not urs
    """TO REVIEW FOR CHANNEL CHANGES"""
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
    #get all the collections of a channel
    @action(detail=False, methods=['get'], url_path='channel/(?P<channel_id>\d+)/collections')
    def channel_collections(self, request, channel_id=None):
        channel = get_object_or_404(Channel, id=channel_id)
        collections = Playlist.objects.filter(channel=channel, type=Playlist.COLLECTION)
        
        if request.user.is_authenticated: #show even if something is private if the user is an editor or owner
            collections = collections.filter(
                Q(privacy_status=Playlist.PUBLIC) |
                Q(channel__channelmembership__userID=request.user, 
                  channel__channelmembership__role__in=[ChannelMembership.EDITOR, ChannelMembership.OWNER])
            ).distinct() #distinct to avoid getting duplicates because of the or
        else: #only show public collections
            collections = collections.filter(privacy_status=Playlist.PUBLIC)

        serializer = self.get_serializer(collections, many=True)
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
        if playlist.type == Playlist.COLLECTION:
            if not playlist.channel:
                raise PermissionDenied("This collection is not associated with any channel.")
            
            #check if the user has editor or owner role in the channel
            has_permission = ChannelMembership.objects.filter(
                channelID=playlist.channel,
                userID=user,
                role__in=[ChannelMembership.EDITOR, ChannelMembership.OWNER]
            ).exists()

            if not has_permission:
                raise PermissionDenied("You do not have permission to add media to this collection as you are not a member of this channel.")

            #check if the media belongs to the channel
            media = serializer.validated_data.get('media')
            if media.channelID != playlist.channel:
                raise PermissionDenied("You can only add media that belongs to this channel.")
        elif playlist.created_by != user:
            raise PermissionDenied("You are not the owner of this playlist.")
        #if watch later exists add the media to it, otherwise create it 
        if playlist.type == Playlist.WATCHLATER:
            raise PermissionDenied("Creation of 'Watch Later' playlist is not allowed.")
        '''
        removed and replaced by checking if media belongs to the channel
        if playlist.type == Playlist.COLLECTION:
            media = Media.objects.filter(uploaderID=user)
            if serializer.validated_data['media'] not in media:
                raise PermissionDenied("Cannot add media you do not own to a collection.")'''
        
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
                print(media_id)
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