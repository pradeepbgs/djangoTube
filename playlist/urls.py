from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.createPlaylist, name='create'),
    path('getPlaylist/', views.getPlaylist, name='list'),
    path('add-video/<int:playlistId>/<int:videoId>/', views.updatePlaylist, name='update'),
    path('remove-video/<int:playlistId>/<int:videoId>/', views.removeVideoFromPlaylist, name='delete'),
    path('update/<int:playlistId>/', views.updatePlaylist, name='update'),
    path('delete/<int:playlistId>/', views.deletePlaylist, name='delete'),
]