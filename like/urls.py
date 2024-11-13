from django.urls import path
from . import views

urlpatterns = [
    path('toggle/<int:videoId>/',views.toggle_video_like,name='togglevideolike'),
    path('toggle-comment/<int:commentId>/',views.toggle_comment_like,name='togglecommentlike'),
    path('liked-videos/',views.get_liked_videos,name='getlikedvideos')
]