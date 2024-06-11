from ..users.permissions import IsAdmin
from rest_framework import viewsets
from .models import Video, Transcript, VideoSegment
from .serializers import VideoSerializer, TranscriptSerializer, VideoSegmentSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdmin]


class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAdmin]

class VideoSegmentViewSet(viewsets.ModelViewSet):
    queryset = VideoSegment.objects.all()
    serializer_class = VideoSegmentSerializer
    permission_classes = [IsAdmin]
