# myapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

 

class User(AbstractUser):
    ADMIN = 'admin'
    SUBSCRIBED_USER = 'subscribed_user'
    NORMAL_USER = 'normal_user'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (SUBSCRIBED_USER, 'Subscribed User'),
        (NORMAL_USER, 'Normal User'),
    ]

    phone_number = models.CharField(max_length=20, unique=False, default='Unknown')
    address = models.CharField(max_length=255, blank=True)
    linkedinurl = models.URLField(max_length=255, blank=True)
    # jobs = models.ManyToManyField('joblistings.Job', related_name='users', blank=True)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=NORMAL_USER
    )
    picture = models.ImageField(upload_to='profile_pictures/%Y/%m/%d/', null=True, blank=True)

    def __str__(self):
        return self.username
