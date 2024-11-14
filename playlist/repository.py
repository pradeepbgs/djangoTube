import traceback
from asgiref.sync import sync_to_async
from .models import PlaylistModel
from django.db.models import Prefetch
from video.models import VideoModel

class PlaylistRepository:

    @staticmethod
    @sync_to_async
    def createPlaylist(playlistName,playlistDescription,user):
        try:
            return PlaylistModel.objects.create(
                name = playlistName,
                description = playlistDescription,
                owner = user
            )
        except:
            traceback.print_exc()
            return None

    @staticmethod
    @sync_to_async
    def savePlaylist(playlist):
        try:
            return playlist.save()
        except:
            traceback.print_exc()
            return None

    @staticmethod
    @sync_to_async
    def getPlaylistWithVideos(id,user,offset,limit):
        try:
            playlist = (
                PlaylistModel.objects.filter(id=id)
                .prefetch_related(
                    Prefetch(
                        'videos',
                        queryset=VideoModel.objects.filter(owner=user)
                        .select_related('owner')
                        .order_by('created_at')[offset:offset+limit]
                    )
                )
                .select_related('owner')
            )
            return playlist if playlist else None
        except:
            traceback.print_exc()
            return None
    
    @staticmethod
    @sync_to_async
    def getPlaylistVideos(playlist,offset,limit):
        try:
            videos = (
                playlist.videos.all()
                .select_related('owner')
                .order_by('created_at')[offset:offset+limit]
                )
            return list(videos) if videos else None
        except:
            traceback.print_exc()
            return None
    
    @staticmethod
    @sync_to_async
    def getPlaylistById(id):
        try:
            playlist = PlaylistModel.objects.get(id=id)
            return playlist if playlist else None
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def getUserPlaylist(id,user):
        try:
            playlist = PlaylistModel.objects.get(id=id,owner=user)
            return playlist if playlist else None
        except:
            print(traceback.format_exc())
            return None
    
    @staticmethod
    @sync_to_async
    def deletePlaylist(playlistId,user):
        try:
            playlist = PlaylistModel.objects.get(id=playlistId, owner=user)
            if playlist:
                playlist.delete()
                return playlist
            return None
        except:
            traceback.print_exc()
            return None