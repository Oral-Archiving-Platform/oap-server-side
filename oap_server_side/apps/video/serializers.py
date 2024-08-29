from rest_framework import serializers
from .models import Video, Transcript, VideoSegment,Participant
from ..media.serializers import MediaSerializer

class VideoSerializer(serializers.ModelSerializer):

    media_details = MediaSerializer(source='mediaID', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        media_representation = MediaSerializer(instance.mediaID).data
        representation['media_details'] = media_representation
        return representation
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            return obj.mediaID.is_liked_by_user(user)
        return False
        
class VideoPageSerializer(serializers.ModelSerializer):

    media_details = MediaSerializer(source='mediaID', read_only=True)


    class Meta:
        model = Video
        fields = ['id','videoURL','media_details']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        media_representation = MediaSerializer(instance.mediaID).data
        representation['media_details'] = media_representation
        return representation
    
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = '__all__'

class VideoSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSegment
        fields = '__all__'
