from django.db import models
from apps.users.models import User
from apps.media.models import Media

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by= models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PlaylistMedia(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.playlist.name + ' - ' + self.media.title