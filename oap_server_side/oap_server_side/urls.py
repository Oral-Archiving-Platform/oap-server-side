
from django.contrib import admin
from django.urls import path,include
from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('api/m/', include('apps.media.urls')),
    path('api/v/', include('apps.video.urls')),
    path('api/u/', include('apps.users.urls')),

]
