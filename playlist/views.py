from django.shortcuts import render
from django.http import JsonResponse
from utils.auth import verify_jwt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .repository import PlaylistRepository
import traceback
# Create your views here.

@csrf_exempt
@verify_jwt
async def createPlaylist(request):
    if request.method != 'POST':
        return JsonResponse({'success':False,'message': 'Invalid request method'}, status=400)
    
    if not request.user:
        return JsonResponse({'success':False,'message':'Unauthorized'},status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        playlistName = request.POST.get('playlistName')
        if not playlistName:
            return JsonResponse({'success':False, 'message':'Playlist name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        playlistDescription = request.POST.get('playlistDescription',f"create by {request.user.username}")

        createdPlaylist = await PlaylistRepository.createPlaylist(playlistName, playlistDescription, request.user)
        if not createdPlaylist:
            return JsonResponse({'success':False, 'message':'Failed to create playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        await PlaylistRepository.savePlaylist(createdPlaylist)
        data = {
            'id': createdPlaylist.id,
            'name': createdPlaylist.name,
            'description': createdPlaylist.description,
            'owner': createdPlaylist.owner.id
        }
        return JsonResponse({'success':True, 'message':'Playlist created successfully', 'data':data},status=status.HTTP_201_CREATED)
    
    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to create playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@verify_jwt
async def getPlaylist(request, id):
    if request.method != 'GET':
        return JsonResponse({'success':False, 'message': 'Invalid request method'}, status=400)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = ( page- 1 ) * limit

        playlist = await PlaylistRepository.getPlaylistWithVideos(id, request.user, offset, limit)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)
        
        playlistdata = {
                "id": playlist.id,
                "name": playlist.name,
                "description": playlist.description,
                "owner": {
                    "username": playlist.owner.username,
                    "profilePicture": playlist.owner.avatar if playlist.owner.avatar else None
                },
                'videos':[
                    {
                        "id": video.id,
                        "title": video.title,
                        "thumbnail": video.thumbnail,
                        "created_at": video.created_at,
                        "owner": {
                            "username": video.owner.username,
                            "profilePicture": video.owner.avatar if video.owner.avatar else None
                        }
                    }
                    for video in playlist.videos.all()
                ]
        }
        return JsonResponse({'success':True, 'message':'Playlist fetched successfully', 'data':playlistdata}, status=status.HTTP_200_OK)
    
    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False, 'message':'Failed to fetch playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@verify_jwt
async def addVideoToPlaylist(request, playlistId,videoId):
    if request.method != 'POST':
        return JsonResponse({'success':False, 'message': 'Invalid request method'}, status=400)

    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not videoId:
            return JsonResponse({'success':False, 'message':'Video id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getPlaylistById(id, request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        playlist.videos.add(videoId)
        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Video added to playlist successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to add video to playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@verify_jwt
async def removeVideoFromPlaylist(request, playlistId, videoId):
    if request.method != 'DELETE':
        return JsonResponse({'success':False, 'message': 'Invalid request method'}, status=400)

    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not videoId:
            return JsonResponse({'success':False, 'message':'Video id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getPlaylistById(id, request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        playlist.videos.remove(videoId)
        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Video removed from playlist successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to remove video from playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@verify_jwt
async def updatePlaylist(request, playlistId):
    if request.method != 'PUT':
        return JsonResponse({'success':False, 'message': 'Invalid request method'}, status=400)

    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getPlaylistById(id, request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        playlistName = request.POST.get('playlistName')
        playlistDescription = request.POST.get('playlistDescription')

        if playlistName:
            playlist.name = playlistName
        if playlistDescription:
            playlist.description = playlistDescription

        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Playlist updated successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to update playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@verify_jwt
async def deletePlaylist(request, playlistId):
    if request.method != 'DELETE':
        return JsonResponse({'success':False, 'message': 'Invalid request method'}, status=400)

    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        deletedPlaylist = await PlaylistRepository.deletePlaylist(playlistId,request.user)

        if not deletedPlaylist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse({'success':True, 'message':'Playlist deleted successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to delete playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)