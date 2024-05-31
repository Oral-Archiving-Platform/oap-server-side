from .views import VideoViewSet, TranscriptViewSet, VideoSegmentViewSet
from .uploadvid import FileUploadView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video ')
router.register(r'segment', VideoSegmentViewSet,basename='segment')
router.register(r'transcript', TranscriptViewSet,basename='transcript')
urlpatterns = [
    path('', include(router.urls)),
]