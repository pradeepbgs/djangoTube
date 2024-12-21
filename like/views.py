from django.views.decorators.csrf import csrf_exempt
from utils.auth import verify_jwt
import traceback
from .repository import LikeRepository
from video.repository import VideoRepository
from comment.repository import CommentRepository
from django.http import JsonResponse
from rest_framework import status
from django.views.decorators.http import require_POST,require_GET
from asgiref.sync import sync_to_async

# Create your views here.
#toggle video like
@require_POST
@csrf_exempt
@verify_jwt
async def toggle_video_like(request,videoId)-> JsonResponse:
    if not request.user:
        return JsonResponse({'success':False,'message':'unauthorized'},status=401)
    
    try:
        
        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({'success':False, 'message':'could not find the video'}, status=404)
        
        like_status = await LikeRepository.toggleLike(request.user,video)

        if like_status == 'liked':
            message = 'Video liked successfully'
        else:
            message = 'Video unliked successfully'

        return JsonResponse({'success': True, 'message': message}, status=200)
        
    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False,'message':'something went wrong'},status=500)

#toggle comment like
@require_POST
@verify_jwt
async def toggle_comment_like(request, commentId)-> JsonResponse:
    if not request.user:
        return JsonResponse({'success':False, 'message':'unauthorized'}, status=401)

    try:

        comment = await CommentRepository.getCommentByCommentId(commentId)
        if not comment:
            return JsonResponse({'success':False, 'message':'could not find the comment'}, status=404)

        like_status = await LikeRepository.toggleCommentLike(request.user,comment)

        if like_status == 'liked':
            message = 'Comment liked successfully'
        else:
            message = 'Comment unliked successfully'

        return JsonResponse({'success': True, 'message': message}, status=200)

    except:
        print(traceback.format_exc())
        return JsonResponse({'success':False, 'message':'something went wrong'}, status=500)

#get liked videos
@require_GET
@verify_jwt
async def get_liked_videos(request)-> JsonResponse:
    if not request.user:
        return JsonResponse({'success':False, 'message':'unauthenticated'}, status=401)

    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page-1)*limit

        liked_videos = await LikeRepository.getLikedVideos(request.user,offset,limit)
        if not liked_videos:
            return JsonResponse({'success':True, 'message':'there are no liked video','data':[]}, status=status.HTTP_404_NOT_FOUND)
        

        data = []
        for like in liked_videos:
            video = like.video
            owner = await sync_to_async(lambda: video.owner)()
            data.append({
                'id': video.id,
                'title': video.title,
                'url': video.video_file,
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