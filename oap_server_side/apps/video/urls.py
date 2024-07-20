from .views import VideoViewSet, TranscriptViewSet, VideoSegmentViewSet, ParticipantViewSet,complexSegementViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video ')
router.register(r'segment', VideoSegmentViewSet,basename='segment')
router.register(r'transcript', TranscriptViewSet,basename='transcript')
router.register(r'participant', ParticipantViewSet,basename='participant')
router.register(r'combined', complexSegementViewSet,basename='combined')


urlpatterns = [
    path('', include(router.urls)),
    
]