from django.http import JsonResponse
from utils.auth import verify_jwt
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .repository import PlaylistRepository
import traceback
from asgiref.sync import sync_to_async
# Create your views here.

@require_POST
@csrf_exempt
@verify_jwt
async def createPlaylist(request):
    if not request.user:
        return JsonResponse({'success':False,'message':'Unauthorized'},status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        playlistName = request.POST.get('playlistName', None)
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

@require_GET
@verify_jwt
async def getPlaylist(request, id):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        if not id:
            return JsonResponse({'success': False, 'message': 'Please provide playlist id'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getPlaylistById(id)
        if not playlist:
            return JsonResponse({'success': False, 'message': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        videos = await PlaylistRepository.getPlaylistVideos(playlist, offset, limit)
        if videos is None:
            return JsonResponse({'success': False, 'message': 'No videos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        playlistOwner = await sync_to_async(lambda: playlist.owner)()

        videos_data = []
        for video in videos:
            owner = await sync_to_async(lambda: video.owner)()
            videos_data.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "thumbnail": video.thumbnail,
                "videoFile": video.video_file,
                "owner": {
                    "username": owner.username,
                    "avatar": owner.avatar if owner.avatar else None
                },
                "createdAt": video.created_at
            })

        playlistdata = {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "owner": {
                "username": playlistOwner.username,
                "profilePicture": playlistOwner.avatar if playlistOwner.avatar else None
            },
            "videos": videos_data
        }

        return JsonResponse({'success': True, 'message': 'Playlist fetched successfully', 'data': playlistdata}, status=status.HTTP_200_OK)

    except Exception:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': 'Failed to fetch playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_POST
@csrf_exempt
@verify_jwt
async def addVideoToPlaylist(request, playlistId,videoId):
    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not videoId:
            return JsonResponse({'success':False, 'message':'Video id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getUserPlaylist(playlistId,request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        await sync_to_async(playlist.videos.add)(videoId)
        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Video added to playlist successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to add video to playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_http_methods(['DELETE'])
@csrf_exempt
@verify_jwt
async def removeVideoFromPlaylist(request, playlistId, videoId):
    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not videoId:
            return JsonResponse({'success':False, 'message':'Video id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getUserPlaylist(playlistId, request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        await sync_to_async(playlist.videos.remove)(videoId)
        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Video removed from playlist successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to remove video from playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

require_POST
@csrf_exempt
@verify_jwt
async def updatePlaylist(request, playlistId):
    if not request.user:
        return JsonResponse({'success':False, 'message':'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if not playlistId:
            return JsonResponse({'success':False, 'message':'playlist id is required'}, status=status.HTTP_400_BAD_REQUEST)

        playlist = await PlaylistRepository.getUserPlaylist(playlistId, request.user)
        if not playlist:
            return JsonResponse({'success':False, 'message':'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        playlistName = request.POST.get('playlistName')
        playlistDescription = request.POST.get('description')

        if playlistName:
            playlist.name = playlistName
        if playlistDescription:
            playlist.description = playlistDescription

        await PlaylistRepository.savePlaylist(playlist)

        return JsonResponse({'success':True, 'message':'Playlist updated successfully'}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to update playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_http_methods(['DELETE'])
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