from django.http import JsonResponse
from utils.auth import verify_jwt
from django.views.decorators.http import require_POST,require_GET,require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .repository import PlaylistRepository
import traceback
from asgiref.sync import sync_to_async
from user.repository import UserRepository
import json
# Create your views here.

@require_POST
@csrf_exempt
@verify_jwt
async def createPlaylist(request):
    if not request.user:
        return JsonResponse({'success':False,'message':'Unauthorized'},status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        data = json.loads(request.body)
        playlistName = data.get('playlistName', None)
        if not playlistName or not len(playlistName):
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
async def getUserPlayList(request, id):
    try:
        if not id:
            return JsonResponse({'success': False, 'message': 'Please provide userid id'}, status=status.HTTP_400_BAD_REQUEST)
# 
        user = await UserRepository.getUserById(id)
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        playlists = await PlaylistRepository.getUserPlaylist(user)
        if not playlists:
            return JsonResponse({'success': True, 'message': 'Playlist not found','data':[]}, status=status.HTTP_404_NOT_FOUND)

        # playlistOwner = await sync_to_async(lambda: playlists.owner)()
        playlistdata = [
            {
                'id': playlist.id,
                'name': playlist.name,
                'description': playlist.description,
                'createdAt': playlist.created_at,
                'owner': {
                    'id': playlist.owner.id,
                    'username': playlist.owner.username,
                    'avatar': playlist.owner.avatar,
                } if playlist.owner else None
            } for playlist in playlists
        ] if playlists else []
        
        return JsonResponse({'success': True, 'message': 'Playlist fetched successfully', 'data': playlistdata}, status=status.HTTP_200_OK)

    except Exception:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': 'Failed to fetch playlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@require_GET
@verify_jwt
async def getPlayListById(request,id):
    try:
        if not id:
            return JsonResponse({'success':False, 'message':'Please provide playlist id'}, status=status.HTTP_400_BAD_REQUEST)
        
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        videos = await PlaylistRepository.getPlaylistVideos(id,offset,limit)
        if not videos:
            return JsonResponse({'success':True, 'message':'No videos found','data':[]}, status=status.HTTP_200_OK)
        
        video_data = [
            {
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'thumbnail': video.thumbnail,
                'videoFile': video.video_file,
                'duration': video.duration,
                'owner': {
                    'id': video.owner.id,
                    'username': video.owner.username,
                    'avatar': video.owner.avatar
                },
                'createdAt': video.created_at
            }
            for video in videos
        ] if videos else []

        return JsonResponse({'success':True, 'message':'Playlists videos fetched successfully', 'data':video_data}, status=status.HTTP_200_OK)

    except:
        traceback.print_exc()
        return JsonResponse({'success':False, 'message':'Failed to fetch playlists videos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        playlist = await PlaylistRepository.getUserPlaylistById(playlistId,request.user)
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

        playlist = await PlaylistRepository.getUserPlaylistById(playlistId, request.user)
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
@csrf_exempt
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
