from django.contrib import admin
from .models import Video, Transcript, VideoSegment
# Register your models here.

admin.site.register(Video)
admin.site.register(Transcript)
admin.site.register(VideoSegment)