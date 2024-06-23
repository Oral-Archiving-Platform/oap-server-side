from rest_framework import serializers
from .models import Video, Transcript, VideoSegment
from ..media.serializers import MediaSerializer
from ..media.models import Media

class VideoSerializer(serializers.ModelSerializer):
    mediaID = serializers.PrimaryKeyRelatedField(
        queryset=Media.objects.all(),
        write_only=True
    )
    media_details = MediaSerializer(source='mediaID', read_only=True)

    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        """ Modify the output to include detailed media info."""
        representation = super().to_representation(instance)
        media_representation = MediaSerializer(instance.mediaID).data
        representation['media_details'] = media_representation
        return representation
    
    

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'

class VideoSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSegment
        fields = '__all__'
