from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 1
    USER= 0

    phone_number = models.CharField(max_length=20) 
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,  
    )

    def __str__(self):
        return self.username