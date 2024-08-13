from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django_otp.models import Device

class User(AbstractUser):
    ADMIN = '1'
    USER = '0'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
    ]

    phone_number = models.CharField(max_length=20)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default=USER,
    )

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='usergroups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='userpermission',
    )
    is_2fa_completed = models.BooleanField(default=False, editable=False)
    date_of_birth = models.DateField(default=timezone.now)

    def __str__(self):
        return self.username
