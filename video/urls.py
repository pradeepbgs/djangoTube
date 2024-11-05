from django.urls import path
from . import views

urlpatterns = [
    path("get-videos/", views.get_all_videos,name='getallvideos'),
    path('upload/',views.upload_video,name='uploadvideo')
]