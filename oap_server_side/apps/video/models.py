from django.db import models
from apps.users.models import User
from apps.media.models import Media
import datetime

class Video(models.Model):
    PUB='1'
    UNL='2'
    PRIV='0'
    VIS_CHOICES = [
        (PUB, 'Public'),
        (UNL, 'Unlisted'),
        (PRIV, 'Private'),
    ]

    A='1'
    N='0'
    RES_CHOICES = [
        (N, 'None'),
        (A, 'Age restricted'),
    ] #to modify depending on what is required

    visibility=models.CharField(
        max_length=50,
        choices=VIS_CHOICES,
        default=PUB,  
    )
    restriction=models.CharField(
        max_length=50,
        choices=RES_CHOICES,
        default=N,  
    ) #idk what it means
    interviewDate = models.DateField(default=datetime.date.today)
    interviewee= models.CharField(max_length=100,default="")
    interviewer= models.CharField(max_length=100,default="")
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    videoURL = models.URLField()
    thumbnailURL = models.URLField()
    duration = models.DurationField()
    size = models.FloatField()

    def __str__(self):
        return self.videoURL

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
