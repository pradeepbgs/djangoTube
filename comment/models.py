from django.db import models
from video.models import VideoModel
from django.conf import settings


# Create your models here.

class CommentModel(models.Model):
    comment = models.CharField(max_length=50)
    video = models.ForeignKey(VideoModel,on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    