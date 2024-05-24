from django.db import models
from apps.models.users import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Media(models.Model):
    VIDEO=1
    OTHER=2
    ROLE_CHOICES = [
        (VIDEO, 'Video'),
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
    originalLanguage = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Comment(models.Models):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commentDate = models.DateTimeField()

    def __str__(self):
        return self.content
    
class View(models.Models):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    viewDate = models.DateTimeField()

    def __str__(self):
        return self.viewDate
    
