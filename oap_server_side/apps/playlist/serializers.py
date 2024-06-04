from rest_framework import serializers
from .models import Playlist, PlaylistMedia

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
    

class PlaylistMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistMedia
        fields = '__all__'

