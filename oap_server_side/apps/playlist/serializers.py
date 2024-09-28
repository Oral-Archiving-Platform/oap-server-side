from rest_framework import serializers
from .models import Playlist, PlaylistMedia
from apps.video.models import Video
from apps.video.serializers import VideoSerializer
import logging
from apps.media.models import Media

logger = logging.getLogger(__name__)

class PlaylistSerializer(serializers.ModelSerializer):
    playlistThumbnail = serializers.SerializerMethodField(read_only=True)  # Thumbnail for the playlist
    videoCount = serializers.SerializerMethodField(read_only=True)  # Count of videos in the playlist

    class Meta:
        model = Playlist
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def validate(self, data):
        if data.get('type') == Playlist.COLLECTION and not data.get('channel'):
            raise serializers.ValidationError("Collections must be associated with a channel.")
        if data.get('type') != Playlist.COLLECTION and data.get('channel'):
            raise serializers.ValidationError("Only collections can be associated with a channel.")
        return data
    def get_playlistThumbnail(self, obj):
        # Use the correct related_name 'playlist_media_set'
        playlist_media = obj.playlist_media_set.all()  # Corrected related_name
        if playlist_media.exists():
            first_video = playlist_media.first().media.video_media.first()  # Assuming 'video_media' is related
            if first_video:
                return first_video.videoURL  # Access the videoURL from the video details
        return None  # Return None if no video or URL is found
    def get_videoCount(self, obj):
        return obj.playlist_media_set.count()


class PlaylistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'type', 'privacy_status']

class MediaAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistMedia
        fields = ['playlist', 'media']

class PlaylistMediaSerializer(serializers.ModelSerializer):
    video_details = serializers.SerializerMethodField(read_only=True)  # Only for reading
    playlistThumbnail = serializers.SerializerMethodField(read_only=True)  # Thumbnail for the playlist

    class Meta:
        model = PlaylistMedia
        fields = ['playlist', 'media', 'added_at', 'added_by', 'video_details', 'playlistThumbnail']
        read_only_fields = ['added_at', 'added_by']

    def get_video_details(self, obj):
        # Assuming the related_name for the ForeignKey from Video to Media is 'mediaID'
        video = obj.media.video_media.first()  # Adjust this logic as needed
        if video:
            return VideoSerializer(video).data
        return None

    def get_playlistThumbnail(self, obj):
        # Use the correct related_name 'playlist_media_set'
        playlist_media = obj.playlist.playlist_media_set.all()  # Corrected related_name
        if playlist_media.exists():
            first_video = playlist_media.first().media.video_media.first()  # Assuming 'video_media' is related
            if first_video:
                return first_video.videoURL  # Access the videoURL from the video details
        return None  # Return None if no video or URL is found



class PlaylistDetailSerializer(serializers.ModelSerializer):
    playlist_media = PlaylistMediaSerializer(many=True, read_only=True, source='playlist_media_set')
    
    logger.info("PlaylistDetailSerializer")

    class Meta:
        model = Playlist
        fields = ['name', 'description', 'created_by', 'created_at', 'updated_at', 'created_by', 'type', 'privacy_status', 'playlist_media']

class AddToWatchLaterSerializer(serializers.Serializer):
    media_id = serializers.IntegerField()

    def validate_media_id(self, value):
        if not Media.objects.filter(id=value).exists():
            raise serializers.ValidationError("Media with this ID does not exist.")
        return value
