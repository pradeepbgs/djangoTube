import traceback
from asgiref.sync import sync_to_async
from .models import PlaylistModel

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
    def getPlaylist(id):
        try:
            return PlaylistModel.objects.get(id=id)
        except:
            traceback.print_exc()
            return None
    
    