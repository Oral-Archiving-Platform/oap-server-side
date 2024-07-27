from .views import VideoViewSet, TranscriptViewSet, VideoSegmentViewSet, ParticipantViewSet, ComplexSegmentViewSet, complexSegementViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video')
router.register(r'segment', VideoSegmentViewSet, basename='segment')
router.register(r'transcript', TranscriptViewSet, basename='transcript')
router.register(r'participant', ParticipantViewSet, basename='participant')
router.register(r'combined', complexSegementViewSet, basename='combined')

urlpatterns = [
    path('', include(router.urls)),
    path('videos/<int:video_id>/add_interviewers/', ParticipantViewSet.as_view({'post': 'add_participant'}), name='add_participant'),
    path('videos/participants/by_role_and_video/', ParticipantViewSet.as_view({'get': 'retrieve_by_role'}), name='get_participants_by_role'),
    path('videos/<int:video_id>/add-segments/', VideoSegmentViewSet.as_view({'post': 'create_video_segment'}), name='create_video_segment'),
    path('videos/<int:video_id>/segments/', VideoSegmentViewSet.as_view({'get': 'get_segments'}), name='get_video_segments'),
    path('videos/<int:video_id>/transcripts/', TranscriptViewSet.as_view({'get': 'get_transcripts'}), name='get_video_transcripts'),
    path('videos/<int:video_id>/transcripts/create/', TranscriptViewSet.as_view({'post': 'create_transcripts'}), name='create_transcripts'),
    path('videos/<int:video_id>/segments-and-transcripts/create/', ComplexSegmentViewSet.as_view({'post': 'create_complex_segment'}), name='create_complex_segment'),
]
