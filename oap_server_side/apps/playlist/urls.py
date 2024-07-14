from .views import PlaylistViewSet, PlaylistMediaViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include
router = DefaultRouter()
router.register(r'playlist', PlaylistViewSet, basename='playlist')
router.register(r'playlist_media', PlaylistMediaViewSet,basename='playlist_media')



urlpatterns = [
    path('', include(router.urls)),
    path('playlist/user_playlists/', PlaylistViewSet.as_view({'get': 'user_playlists'}), name='user_playlists'),
    path('playlist/user_media/', PlaylistViewSet.as_view({'get': 'user_media'}), name='user_media'),

]



