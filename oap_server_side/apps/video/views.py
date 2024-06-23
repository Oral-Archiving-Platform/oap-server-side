from ..users.permissions import IsAdmin
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Video, Transcript, VideoSegment
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [AllowAny]
    
    

class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAdmin]

class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
    permission_classes = [IsAdmin]
