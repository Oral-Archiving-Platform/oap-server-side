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
        return f"{self.userID.email} - {self.get_role_display()} of {self.channelID.name}"

    
class Subscription(models.Model):
    channelID = models.ForeignKey(Channel, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    subscriptionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Subscription"
    

class CollaborationInvitation(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    invitee_email = models.EmailField()
    role = models.CharField(max_length=50, choices=ChannelMembership.ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=100, unique=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation for {self.invitee_email} to {self.channel.name}"
