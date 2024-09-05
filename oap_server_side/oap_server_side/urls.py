from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Include paths for API endpoints and the admin site
urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel URL
    # path('accounts/', include('django.contrib.auth.urls')), 

    # API endpoints for various apps
    path('api/m/', include('apps.media.urls')),        # Media-related APIs
    path('api/v/', include('apps.video.urls')),        # Video-related APIs
    path('api/u/', include('apps.users.urls')),        # User-related APIs
    path('api/p/', include('apps.playlist.urls')),     # Playlist-related APIs
    path('api/c/', include('apps.channel.urls')),      # Channel-related APIs
    path('api/e/', include('apps.ebooks.urls')),       # Ebooks-related APIs
]

# Serve static and media files during development
if settings.DEBUG:  # Only serve these in debug mode (development)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
