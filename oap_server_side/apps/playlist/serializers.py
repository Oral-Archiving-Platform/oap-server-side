from rest_framework import serializers
from .models import Playlist, PlaylistMedia
from apps.video.models import Video
from apps.video.serializers import VideoSerializer
import logging

logger = logging.getLogger(__name__)

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
    

class PlaylistMediaSerializer(serializers.ModelSerializer):
    video_details = serializers.SerializerMethodField(read_only=True)# Only for reading
    class Meta:
        model = PlaylistMedia
        fields = ['playlist', 'media', 'added_at', 'added_by', 'video_details']

    def get_video_details(self, obj):
        # Assuming the related_name for the ForeignKey from Video to Media is 'mediaID'
        # Adjust this if the related_name is differently defined
        video = obj.media.video_media.first() #find a better way to handl ethis
        if video:
            return VideoSerializer(video).data
        return None



class PlaylistDetailSerializer(serializers.ModelSerializer):
    playlist_media = PlaylistMediaSerializer(many=True, read_only=True, source='playlist_media_set')
    logger.info("PlaylistDetailSerializer")
    class Meta:
        model = Playlist
        fields = ( 'name','description','created_by','created_at', 'updated_at','created_by','type', 'privacy_status', 'playlist_media')


class AddToWatchLaterSerializer(serializers.Serializer):
    media_id = serializers.IntegerField()

    def validate_media_id(self, value):
        if not PlaylistMedia.objects.filter(id=value).exists():
            raise serializers.ValidationError("Media with this ID does not exist.")
        return value