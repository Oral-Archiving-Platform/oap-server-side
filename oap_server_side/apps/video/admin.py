from django.contrib import admin
from .models import Video, Transcript, VideoSegment, Participant, Topic, ImportantPerson,City,Monument
# Register your models here.

admin.site.register(Video)
admin.site.register(Transcript)
admin.site.register(VideoSegment)
admin.site.register(Participant)
admin.site.register(City)
admin.site.register(Monument)
admin.site.register(Topic)
admin.site.register(ImportantPerson)
