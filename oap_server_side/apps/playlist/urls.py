from .views import PlaylistViewSet, PlaylistMediaViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'playlist', PlaylistViewSet, basename='playlist')
router.register(r'playlist_media', PlaylistMediaViewSet,basename='playlist_media')



urlpatterns = [
    path('', include(router.urls)),
    #path('playlist/user_media/', PlaylistViewSet.as_view({'get': 'user_media'}), name='user_media'),
    #path('playlist/all_media/',PlaylistMediaViewSet.as_view({'get':'get_channel_videos'}),name='get_channel_videos'),
    path('playlist/playlist_by_role/', PlaylistViewSet.as_view({'get': 'get_playlist_by_Role'}), name='get_playlist_by_Role')
]   



