from rest_framework import serializers
from .models import Video, Transcript, VideoSegment,Participant,City, Monument,Topic,ImportantPerson
from ..media.serializers import MediaSerializer
from .utils import create_or_get_topic, create_or_get_important_person

class TopicField(serializers.Field):
    def to_representation(self, value):
        return [topic.name for topic in value.all()]

    def to_internal_value(self, data):
        return [create_or_get_topic(name)[0] for name in data]

class ImportantPersonField(serializers.Field):
    def to_representation(self, value):
        return [person.name for person in value.all()]

    def to_internal_value(self, data):
        return [create_or_get_important_person(name)[0] for name in data]

class VideoSerializer(serializers.ModelSerializer):
    media_details = MediaSerializer(source='mediaID', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    topics = TopicField()
    important_persons = ImportantPersonField()

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
        if request and hasattr(request, 'user'):
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

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class MonumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monument
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
class ImportantPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantPerson
        fields = '__all__'