from rest_framework import serializers
from .models import Video, Transcript, VideoSegment,Participant,City, Monument,Topic,ImportantPerson
from ..media.serializers import MediaSerializer
from .utils import create_or_get_topic, create_or_get_important_person
from ..playlist.models import *

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
class TranscriptSerializer(serializers.ModelSerializer):
    transcriptionLanguage = serializers.CharField(source='transcriptionLanguage.language', read_only=True)

    class Meta:
        model = Transcript
        fields = '__all__'
        
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class MonumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Monument
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.city:
            representation['city'] = CitySerializer(instance.city).data
        
        return representation


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
class ImportantPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantPerson
        fields = '__all__'
class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    media_details = MediaSerializer(source='mediaID', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    topics = TopicField()
    important_persons = ImportantPersonField()
    transcripts = TranscriptSerializer(source='transcript_set', many=True, read_only=True)
    city= CitySerializer(read_only=True)
    monument = MonumentSerializer(read_only=True)
    participants = ParticipantSerializer(source='participants_set', many=True, read_only=True)
    collection_name = serializers.SerializerMethodField(read_only=True)
    collection_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        media_representation = MediaSerializer(instance.mediaID).data
        representation['media_details'] = media_representation
        print("Monument in representation:", representation.get("monument"))
        if not representation.get("monument") and instance.monument:
            # If monument is not present in the representation but exists in instance, add it manually
            representation["monument"] = MonumentSerializer(instance.monument).data

        return representation
    def get_collection_id(self, obj):
        # Get the collection ID if it exists
        try:
            playlist_media = PlaylistMedia.objects.filter(media=obj.mediaID).first()
            if playlist_media and playlist_media.playlist.type == '1':  # Check if it's a collection type
                return playlist_media.playlist.id
        except PlaylistMedia.DoesNotExist:
            return None
        return None
    def get_collection_name(self, obj):
        # Get the collection name if it exists
        try:
            playlist_media = PlaylistMedia.objects.filter(media=obj.mediaID).first()
            if playlist_media and playlist_media.playlist.type == '1':  # Check if it's a collection type
                return playlist_media.playlist.name
        except PlaylistMedia.DoesNotExist:
            return None
        return None

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                return obj.mediaID.is_liked_by_user(user)
        return False

class CreateVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        
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
    



class VideoSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSegment
        fields = '__all__'

