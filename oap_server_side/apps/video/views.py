from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Video, Transcript, VideoSegment
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer
from rest_framework.parsers import FileUploadParser

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer

class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
