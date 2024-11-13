from django.urls import path
from . import views

urlpatterns = [
    path("videos/", views.get_all_videos,name='getallvideos'),
    path('upload/',views.upload_video,name='uploadvideo'),
    path('video-details/<int:videoId>/', views.get_video_details, name='getvideodetails'),
    path('user-videos/<int:userId>/',views.get_user_videos,name='get user videos'),
    path('delete/<int:videoId>/',views.delete_video,name='delete'),
    path('update-video-details/<int:videoId>/',views.update_video_details, name='change video details'),
    path('toggle/<int:videoId>/',views.toggle_publish_status,name='toggle')
]