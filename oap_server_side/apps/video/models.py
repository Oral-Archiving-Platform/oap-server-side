from django.db import models
from apps.users.models import User
from apps.media.models import Media,OriginalLanguage
import datetime
from django.core.exceptions import ValidationError
from pytube import YouTube

class City(models.Model):
    city_name = models.CharField(max_length=100)
    city_image = models.ImageField(upload_to='cities/', null=True)

    def __str__(self):
        return self.city_name
class Monument(models.Model):
    monument_name = models.CharField(max_length=100)
    monument_image = models.ImageField(upload_to='monuments/', null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='monuments')

    def __str__(self):
        return self.monument_name
class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
class ImportantPerson(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

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
    ) 
    interviewDate = models.DateField(default=datetime.date.today)
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE,related_name='video_media')
    videoURL = models.URLField()
    duration = models.DurationField(null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    monument = models.ForeignKey(Monument, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    topics = models.ManyToManyField(Topic, related_name='videos')  # Changed to ManyToManyField
    important_persons = models.ManyToManyField(ImportantPerson, related_name='videos')  # Changed to ManyToManyField

    def __str__(self):
        return self.videoURL
    def clean(self):
        if self.city and self.monument:
            raise ValidationError("A video can only be linked to either a city or a monument, not both.")
        if not self.city and not self.monument:
            raise ValidationError("A video must be linked to either a city or a monument.")
    def save(self, *args, **kwargs):
        if not self.duration and self.videoURL:
            try:
                yt = YouTube(self.videoURL)
                self.duration = datetime.timedelta(seconds=yt.length)  # Convert seconds to timedelta
            except Exception as e:
                # raise ValidationError(f"Error fetching video duration: {e}")
                print(f"Error fetching video duration: {e}")
        if not self.id and self.mediaID_id:
            self.id = self.mediaID_id
        super().save(*args, **kwargs)
        

  

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
    videoSegmentID = models.ForeignKey(VideoSegment, on_delete=models.CASCADE, default=None,blank=True, null=True)
    transcription= models.TextField()
    transcriptionLanguage = models.ForeignKey(OriginalLanguage, on_delete=models.CASCADE, related_name='transcripts')

    def __str__(self):
        return self.title


class Participant(models.Model):
    
    INTERVIEWER = 1
    INTERVIEWEE = 2

    ROLE_CHOICES = [
        (INTERVIEWER, 'Interviewer'),
        (INTERVIEWEE, 'Interviewee'),
        ]

    VideoId = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='participants_set') 
    firstName = models.CharField(max_length=255)  
    lastName = models.CharField(max_length=255, blank=True, null=True)  
    phoneNumber = models.CharField(max_length=20, blank=True, null=True)  
    role = models.IntegerField(choices=ROLE_CHOICES)

    def __str__(self):
        return self.firstName
    











    

   
