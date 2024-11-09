from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from utils.auth import verify_jwt
import traceback
from .repository import LikeRepository
from video.repository import VideoRepository
from comment.repository import CommentRepository
from django.http import JsonResponse


# Create your views here.
#toggle video like
@csrf_exempt
@verify_jwt
async def toggle_video_like(request,videoId):
    if request.method != 'POST':
        return JsonResponse({'success':False,'message':'Method not allowed'},status=405)
    
    if not request.user:
        return JsonResponse({'success':False,'message':'unauthorized'},status=401)
    
    try:
        
        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({'success':False, 'message':'could not find the video'}, status=404)
        
        like_status = await LikeRepository.toggleLike(request.user, 1,video)

        if like_status == 'liked':
            message = 'Video liked successfully'
        else:
            message = 'Video unliked successfully'

        return JsonResponse({'success': True, 'message': message}, status=200)
        
    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False,'message':'something went wrong'},status=500)

#toggle comment like
@csrf_exempt
@verify_jwt
async def toggle_comment_like(request, commentId):
    if request.method != 'POST':
        return JsonResponse({'success':False, 'message':'Method not allowed'}, status=405)

    if not request.user:
        return JsonResponse({'success':False, 'message':'unauthorized'}, status=401)

    try:

        comment = await CommentRepository.getCommentByCommentId(commentId)
        if not comment:
            return JsonResponse({'success':False, 'message':'could not find the comment'}, status=404)

        like_status = await LikeRepository.toggleLike(request.user,2)

        if like_status == 'liked':
            message = 'Comment liked successfully'
        else:
            message = 'Comment unliked successfully'

        return JsonResponse({'success': True, 'message': message}, status=200)

    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False, 'message':'something went wrong'}, status=500)

#get liked videos
@csrf_exempt
@verify_jwt
async def get_liked_videos(request):
    if request.method != 'GET':
        return JsonResponse({'success':False, 'message':'Method not allowed'}, status=405)

    if not request.user:
        return JsonResponse({'success':False, 'message':'unauthorized'}, status=401)

    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))

        liked_videos = await LikeRepository.getLikedVideos(request.user)
        if not liked_videos:
            return JsonResponse({'success':True, 'data':[]}, status=200)
        
        paginated_data = await VideoRepository.get_paginated_videos(liked_videos, page, limit)

        data = []
        for like in paginated_data:
            video = like.video
            owner = video.owner
            data.append({
                'id': video.id,
                'title': video.title,
                'url': video.videoFile,
                'thumbnail_url': video.thumbnail,
                'owner': {
                    'id': owner.id,
                    'username': owner.username,
                    'avatar': owner.avatar if owner.avatar else None
                },
                'created_at': video.created_at,
            })
        responseData = {
            'success': True,
            'data': data,
            'page': page,
            'limit': limit,
            'total': len(liked_videos),
        }
        return JsonResponse(responseData, status=200)

    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False, 'message':'something went wrong'}, status=500)