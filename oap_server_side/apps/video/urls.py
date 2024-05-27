from .views import VideoViewSet, TranscriptViewSet, VideoSegmentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video ')
router.register(r'segment', VideoSegmentViewSet,basename='segment')
router.register(r'transcript', TranscriptViewSet,basename='transcript')

urlpatterns = router.urls