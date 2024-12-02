from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.getPlayListById, name='playlists'),
    path('create/', views.createPlaylist, name='create'),
    path('user/<int:id>/', views.getUserPlayList, name='user playlist'),
    path('add-video/<int:playlistId>/<int:videoId>/', views.addVideoToPlaylist, name='update'),
    path('remove-video/<int:playlistId>/<int:videoId>/', views.removeVideoFromPlaylist, name='delete'),
    path('update/<int:playlistId>/', views.updatePlaylist, name='update'),
    path('delete/<int:playlistId>/', views.deletePlaylist, name='delete'),
]