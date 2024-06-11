from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone


class User(AbstractUser):
    ADMIN = '1'
    USER= '0'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,  
    )

    dateOfBirth = models.DateField(default=timezone.now())

    def __str__(self):
        return self.username