from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class VideoModel(models.Model):
    video_file = models.CharField(max_length=300)
    thumbnail = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300, null=True, blank=True)
    duration = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    isPublished = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos', null=True, blank=True)