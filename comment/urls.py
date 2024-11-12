from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:videoId>/',views.add_comment,name='addcomment'),
    path('update/<int:commentId>/', views.update_comment, name='update comment'),
    path('delete/<int:commentId>/', views.delete_comment, name='delete comment'),
    path('video-comments/<int:videoId>/', views.get_video_comments, name='get video comments')
]