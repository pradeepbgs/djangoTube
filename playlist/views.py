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
    