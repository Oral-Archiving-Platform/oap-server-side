from django.shortcuts import render
from rest_framework import viewsets
from .models import PlaylistMedia, Playlist
from .serializers import PlaylistMediaSerializer,PlaylistSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class PlaylistMediaViewSet(viewsets.ModelViewSet):
    queryset = PlaylistMedia.objects.all()
    serializer_class = PlaylistMediaSerializer