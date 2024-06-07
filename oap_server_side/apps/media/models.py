from django.db import models
from apps.users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Media(models.Model):
    VIDEO='1'
    OTHER='2'
    AUDIO='3'
    ROLE_CHOICES = [
        (VIDEO, 'Video'),
        (AUDIO, 'Audio'),
        (OTHER, 'Other'),
    ]

    title = models.CharField(max_length=100)
    uploaderID = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    uploadDate = models.DateTimeField()
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    type=models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=VIDEO,  
    )
    rightsStatement = models.TextField(default="")
    usageStatement = models.TextField(default="")
    acknowledgement = models.TextField(default="")
    userNotes = models.TextField(default="")
    originalLanguage = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Comment(models.Model):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commentDate = models.DateTimeField()

    def __str__(self):
        return self.content
    
class View(models.Model):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    viewDate = models.DateTimeField()

    def __str__(self):
        return self.viewDate
    
