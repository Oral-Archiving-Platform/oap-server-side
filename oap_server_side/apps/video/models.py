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
    location = models.CharField(max_length=100)
    restriction=models.CharField(
        max_length=50,
        choices=RES_CHOICES,
        default=N,  
    ) 
    interviewDate = models.DateField(default=datetime.date.today)
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE,related_name='video_media')
    videoURL = models.URLField()
    duration = models.DurationField(null=True)
    size = models.FloatField(null=True)

    def __str__(self):
        return self.videoURL
    
class VideoSegment(models.Model):
    VideoID = models.ForeignKey(Video, on_delete=models.CASCADE)
    segmentNumber = models.IntegerField()
    startTime = models.DurationField()
    endTime = models.DurationField()
    description = models.TextField() 
    
    def __str__(self):
        return self.segmentNumber
    
class Transcript(models.Model):
    videoID= models.ForeignKey(Video, on_delete=models.CASCADE)
    videoSegmentID = models.ForeignKey(VideoSegment, on_delete=models.CASCADE, default=None)
    title = models.CharField(max_length=100)
    content = models.TextField()
    transcriberID = models.ForeignKey(User, on_delete=models.CASCADE)
    transcriptDate = models.DateTimeField()
    transcription= models.TextField()
    transcriptionLanguage = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Participant(models.Model):
    
    INTERVIEWER = 1
    INTERVIEWEE = 2

    ROLE_CHOICES = [
        (INTERVIEWER, 'Interviewer'),
        (INTERVIEWEE, 'Interviewee'),
        ]

    VideoId = models.ForeignKey('Video', on_delete=models.CASCADE) 
    firstName = models.CharField(max_length=255)  
    lastName = models.CharField(max_length=255, blank=True, null=True)  
    phoneNumber = models.CharField(max_length=20, blank=True, null=True)  
    role = models.IntegerField(choices=ROLE_CHOICES)

    def __str__(self):
        return self.firstName
    











    

   
