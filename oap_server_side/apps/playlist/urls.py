from .views import PlaylistViewSet, PlaylistMediaViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'playlist', PlaylistViewSet, basename='playlist')
router.register(r'playlist_media', PlaylistMediaViewSet,basename='playlist_media')

urlpatterns = router.urls