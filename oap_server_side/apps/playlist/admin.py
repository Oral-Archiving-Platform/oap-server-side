from django.contrib import admin
from .models import Playlist, PlaylistMedia
# Register your models here.

admin.site.register(Playlist)
admin.site.register(PlaylistMedia)