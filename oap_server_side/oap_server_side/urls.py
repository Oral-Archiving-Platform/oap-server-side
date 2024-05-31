
from django.contrib import admin
from django.urls import path,include
from .views import home
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('api/m/', include('apps.media.urls')),
    path('api/v/', include('apps.video.urls')),
    path('api/u/', include('apps.users.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
