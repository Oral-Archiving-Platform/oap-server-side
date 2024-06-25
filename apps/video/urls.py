from .views import VideoViewSet, TranscriptViewSet, VideoSegmentViewSet, AddparticipantViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'video', VideoViewSet, basename='video ')
router.register(r'segment', VideoSegmentViewSet,basename='segment')
router.register(r'transcript', TranscriptViewSet,basename='transcript')
urlpatterns = [
    path('', include(router.urls)),
    path('videos/<int:video_id>/add_interviewers/', views.AddparticipantViewSet.as_view({'post': 'create'}), name='AddparticipantViewSet'),
    path('videos/participants/by-role/', AddparticipantViewSet.as_view({'get': 'by_role'}), name='get_participants_by_role'),
    path('videos/<int:video_id>/add-segments/', VideoSegmentViewSet.as_view({'post': 'create_video_segment'}), name='create_video_segment'),
    path('videos/<int:video_id>/segments/', VideoSegmentViewSet.as_view({'get': 'get_segments'}), name='get_video_segments'),
    path('videos/<int:video_id>/transcripts/', TranscriptViewSet.as_view({'get': 'get_transcripts'}), name='get_video_transcripts'),
    path('videos/<int:video_id>/transcripts/create/', TranscriptViewSet.as_view({'post': 'create_transcripts'}), name='create_transcripts'),
]