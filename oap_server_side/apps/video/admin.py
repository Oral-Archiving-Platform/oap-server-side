from django.contrib import admin
from .models import Video, Transcript, VideoSegment, Participant
# Register your models here.

admin.site.register(Video)
admin.site.register(Transcript)
admin.site.register(VideoSegment)
admin.site.register(Participant)
