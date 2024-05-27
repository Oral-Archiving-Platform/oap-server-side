from django.db import models
from apps.users.models import User
from apps.media.models import Media

class Video(models.Model):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    videoURL = models.URLField()
    thumbnailURL = models.URLField()
    duration = models.DurationField()
    size = models.FloatField()
    def __str__(self):
        return self.name

class Transcript(models.Model):
    videoID = models.ForeignKey(Video, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    transcriberID = models.ForeignKey(User, on_delete=models.CASCADE)
    transcriptDate = models.DateTimeField()
    transcription= models.TextField()
    transcriptionLanguage = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class VideoSegment(models.Model):
    VideoID = models.ForeignKey(Video, on_delete=models.CASCADE)
    segmentNumber = models.IntegerField()
    startTime = models.DurationField()
    endTime = models.DurationField()
    description = models.TextField()
    
    def __str__(self):
        return self.segmentNumber
