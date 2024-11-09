from django.urls import path
from . import views

urlpatterns = [
    path('add-comment',views.add_comment,name='addcomment'),
    path('update-commennt', views.update_comment, name='update comment'),
    path('delete-comment', views.delete_comment, name='delete comment'),
    path('get-video-comments', views.get_video_comments, name='get video comments')
]