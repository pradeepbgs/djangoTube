from django.urls import path
from . import views

urlpatterns = [
    path('toggle-video-like/<int:videoId>/',views.toggle_video_like,name='togglevideolike'),
    path('toggle-comment-like/<int:commentId>/',views.toggle_comment_like,name='togglecommentlike'),
    path('get-liked-videos/',views.get_liked_videos,name='getlikedvideos')
]