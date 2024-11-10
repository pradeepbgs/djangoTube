from django.urls import path
from . import views

urlpatterns = [
    path('add-comment/<int:videoId>/',views.add_comment,name='addcomment'),
    path('update-commennt/<int:commentId>/', views.update_comment, name='update comment'),
    path('delete-comment/<int:commentId>/', views.delete_comment, name='delete comment'),
    path('get-video-comments/<int:videoId>/', views.get_video_comments, name='get video comments')
]