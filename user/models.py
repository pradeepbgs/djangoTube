from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
# Create your models here.

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    admin = models.BooleanField(default=False)
    avatar = models.CharField(max_length=300, blank=True, null=True)
    coverImage = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'user created {self.username}'

    objects = CustomUserManager()