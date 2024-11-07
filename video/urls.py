from django.urls import path
from . import views

urlpatterns = [
    path("get-videos/", views.get_all_videos,name='getallvideos'),
    path('upload/',views.upload_video,name='uploadvideo'),
    path('get-video-details/<int:videoId>/', views.get_video_details, name='getvideodetails'),
    path('get-user-videos/<int:userId>/',views.get_user_videos,name='get user videos'),
]