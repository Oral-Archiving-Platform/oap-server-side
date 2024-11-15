from django.db import models
from ..users.models import User
from ..channel.models import Channel

class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name
class OriginalLanguage(models.Model):
    language = models.CharField(max_length=100, unique=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not OriginalLanguage.objects.exists():
            languages = [
                'English',
                'Arabic',
                'French',
                'Spanish',
                'German'
            ]
            for lang in languages:
                OriginalLanguage.objects.get_or_create(language=lang)


class Media(models.Model):
    VIDEO='1'
    OTHER='2'
    AUDIO='3'
    EBOOK='4'
    TYPE_CHOICES = [
        (VIDEO, 'Video'),
        (AUDIO, 'Audio'),
        (EBOOK, 'Ebook'),
        (OTHER, 'Other'),
    ]

    title = models.CharField(max_length=100)
    uploaderID = models.ForeignKey(User, on_delete=models.CASCADE)
    channelID = models.ForeignKey(Channel, on_delete=models.CASCADE)
    description = models.TextField()
    uploadDate = models.DateTimeField(auto_now_add=True)
    categoryID = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    type=models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        default=VIDEO,  
    )
    acknowledgement = models.TextField()
    originalLanguage = models.ForeignKey(
        OriginalLanguage,
        on_delete=models.CASCADE,
        related_name='media',
        null=True,
    )


    def __str__(self):
        return self.title
    def is_liked_by_user(self, user):
        if user.is_authenticated:
            return self.like_set.filter(userID=user).exists()
        return False


class View(models.Model):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    viewDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "View"
    
class Like(models.Model):
    mediaID = models.ForeignKey(Media, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    likeDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Like"
    
class Comment(models.Model):
    mediaID = models.ForeignKey(Media, related_name='comments',on_delete=models.CASCADE)
    userID = models.ForeignKey(User, related_name='user_comments',on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)#saved just when object is created
    updated = models.DateTimeField(auto_now=True) #changed whenever object saved
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies',on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.body