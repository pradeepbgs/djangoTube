from django.db import models
from django.conf import settings
from video.models import VideoModel

# Create your models here.

class LikeModel(models.Model):
    LIKE_CHOICES = (
        (1, 'Video'),
        (2, 'Comment'),
    )
    content_type = models.IntegerField(choices=LIKE_CHOICES)
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)