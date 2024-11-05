from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
from django.conf import settings

class VideoModel(models.Model):
    video_file = models.CharField(max_length=300)
    thumbnail = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300, null=True, blank=True)
    duration = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    isPublished = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
