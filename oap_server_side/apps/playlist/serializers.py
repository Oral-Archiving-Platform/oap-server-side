from rest_framework import serializers
from .models import Playlist, PlaylistMedia
from apps.video.models import Video
from apps.video.serializers import VideoSerializer
import logging
from apps.media.models import Media

logger = logging.getLogger(__name__)

class PlaylistSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = PlaylistMedia
        fields = ['playlist', 'media', 'added_at', 'added_by', 'video_details']
        read_only_fields = ['added_at', 'added_by']

    def get_video_details(self, obj):
        # Assuming the related_name for the ForeignKey from Video to Media is 'mediaID'
        # Adjust this if the related_name is differently defined
        video = obj.media.video_media.first()  # find a better way to handle this
        if video:
            return VideoSerializer(video).data
        return None

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
