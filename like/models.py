from django.db import models
from django.conf import settings
from video.models import VideoModel
from comment.models import CommentModel
# Create your models here.

class LikeModel(models.Model):
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(CommentModel, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'liked'


class DisLikeModel(models.Model):
    video = models.ForeignKey(VideoModel, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(CommentModel, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'disliked'