from django.db import models
from ..users.models import User


class Channel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creationDate = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='channel_icons/', null=True, blank=True)
    cover = models.ImageField(upload_to='channel_covers/', null=True, blank=True)
    

    def __str__(self):
        return self.name

class ChannelMembership(models.Model):
    EDITOR='1'
    OWNER='2'
    ROLE_CHOICES = [
        (EDITOR, 'Editor'),
        (OWNER, 'Owner'),
    ]
    channelID = models.ForeignKey(Channel, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=OWNER,  
    )
    class Meta:
        unique_together = ('channelID', 'userID')

    def __str__(self):
        return self.role
    
class Subscription(models.Model):
    channelID = models.ForeignKey(Channel, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    subscriptionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Subscription"