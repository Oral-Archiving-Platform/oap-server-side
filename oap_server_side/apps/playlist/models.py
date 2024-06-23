from django.db import models
from apps.users.models import User
from apps.media.models import Media

class Playlist(models.Model):
    PLAYLIST='0'
    COLLECTION='1'
    TYPE_CHOICES = [
        (PLAYLIST, 'Playlist'),
        (COLLECTION, 'Collection'),
    ]
    PUBLIC='0'
    PRIVATE='1'
    PRIV_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by= models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type=models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default=PLAYLIST,  
    )
    privacy_status=models.CharField(
            max_length=50,
            choices=PRIV_CHOICES,
            default=PUBLIC,  
        )
    def __str__(self):
        return self.name

class PlaylistMedia(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE) 
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.playlist.name + ' - ' + self.media.title