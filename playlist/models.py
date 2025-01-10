from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from video.models import VideoModel
# Create your models here.

class PlaylistModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    videos = models.ManyToManyField(VideoModel, related_name='playlists')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='playlists', on_delete=models.CASCADE,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'PlayList created by {self.owner}'