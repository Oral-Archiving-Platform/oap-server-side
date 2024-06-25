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
    
class VideoSegment(models.Model):
    VideoID = models.ForeignKey(Video, on_delete=models.CASCADE)
    segmentNumber = models.IntegerField()
    startTime = models.DurationField()
    endTime = models.DurationField()
    description = models.TextField() 

    def __str__(self):
        return self.segmentNumber



class Transcript(models.Model):
    videoID = models.ForeignKey(Video, on_delete=models.CASCADE)
    VideoSegmentID= models.ForeignKey(VideoSegment, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    transcriberID = models.ForeignKey(User, on_delete=models.CASCADE)
    transcriptDate = models.DateTimeField()
    transcription= models.TextField()
    transcriptionLanguage = models.CharField(max_length=100)

    def __str__(self):
        return self.title


INTERVIEWER = 1
INTERVIEWEE = 2

ROLE_CHOICES = [
    (INTERVIEWER, 'Interviewer'),
    (INTERVIEWEE, 'Interviewee'),
    ]

class Participant(models.Model):
    VideoId = models.ForeignKey('Video', on_delete=models.CASCADE) 
    firstName = models.CharField(max_length=255)  
    lastName = models.CharField(max_length=255, blank=True, null=True)  
    phoneNumber = models.CharField(max_length=20, blank=True, null=True)  
    role = models.IntegerField(choices=ROLE_CHOICES)

    def __str__(self):
        return self.firstName
    











    

   
