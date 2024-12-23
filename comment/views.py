from django.http import JsonResponse
from rest_framework import status
from .repository import CommentRepository
from video.repository import VideoRepository
from utils.auth import verify_jwt
from django.views.decorators.csrf import csrf_exempt
import traceback
from asgiref.sync import sync_to_async
from django.views.decorators.http import require_POST,require_GET,require_http_methods

# Create your views here.

# add comment
@require_POST
@csrf_exempt
@verify_jwt
async def add_comment(request,videoId) -> JsonResponse:
    if not request.user:
        return JsonResponse({"success":False,'message':'unauthorized user'},status=status.HTTP_401_UNAUTHORIZED)

    if not videoId:
        return JsonResponse({"success":False,'message':'pls provide video id'},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        comment = request.POST.get('comment')

        if not comment:
            return JsonResponse({"success":False,'message':'pls provide comment'},status=status.HTTP_401_UNAUTHORIZED)

        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({"success":False,'message':'video not found'},status=status.HTTP_401_UNAUTHORIZED)
        
        savedComment = await CommentRepository.addComment(comment,video,request.user)
        if savedComment:
            return JsonResponse({"success":True,'message':'comment saved successfully'},status=status.HTTP_200_OK)
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False,'message':'got error while adding comment'},status=status.HTTP_400_BAD_REQUEST)


# get video comments by pagination
@require_GET
@verify_jwt
async def get_video_comments(request,videoId) -> JsonResponse :
    if not videoId:
        return JsonResponse({"success":False,'message':'pls provide video id'},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({"success":False,'message':'video doesnt exist'},status=status.HTTP_400_BAD_REQUEST)
        
        videoComments = await CommentRepository.getVideoCommentsByVideo(video,request.user,offset,limit)
        if not videoComments:
            return JsonResponse({"success":False, 'message':'no comments found'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = [{
            'id': comment.id,
            'comment': comment.comment,
            'created_at': comment.created_at,
            'likes': comment.likes_count,
            'is_liked': comment.is_liked,
            'owner': {
                'id': comment.owner.id,
                'username': comment.owner.username
            }
        } for comment in videoComments] if videoComments else None
        
        return JsonResponse({'success':True,'message':'successfully retreived the data','data':data}, status=status.HTTP_200_OK)
    
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False,'message':'got error while retreiving comment'},status=status.HTTP_400_BAD_REQUEST)


#update comment
@require_POST
@csrf_exempt
@verify_jwt
async def update_comment(request , commentId) -> JsonResponse:
    if not request.user:
        return JsonResponse({"success":False, 'message':'unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not commentId:
        return JsonResponse({"success":False, 'message':'pls provide comment id'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        comment_text = request.POST.get('comment')
        if not comment_text:
            return JsonResponse({"success":False, 'message':'pls provide comment'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = await CommentRepository.getCommentByCommentId(commentId)
        if not comment:
            return JsonResponse({"success":False, 'message':'comment doesnt exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment_owner_id = await sync_to_async(lambda: comment.owner.id)()
        if comment_owner_id != request.user.id:
            return JsonResponse({"success":False, 'message':'you are not the owner of this comment'}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment.comment = comment_text
        await sync_to_async(comment.save)()

        return JsonResponse({"success":True, 'message':'comment updated successfully'}, status=status.HTTP_200_OK)
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False, 'message':'something went wrong while updating comment'}, status=status.HTTP_400_BAD_REQUEST)


#delete comment
@require_http_methods(['DELETE'])
@csrf_exempt
@verify_jwt
async def delete_comment(request,commentId)-> JsonResponse:
    if not request.user:
        return JsonResponse({"success":False, 'message':'unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not commentId:
        return JsonResponse({"success":False, 'message':'pls provide comment id'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
            comment = await CommentRepository.getCommentByCommentId(commentId)
            if not comment:
                return JsonResponse({"success":False, 'message':'comment doesnt exist'}, status=status.HTTP_400_BAD_REQUEST)

            comment_owner_id = await sync_to_async(lambda: comment.owner.id)()
            if comment_owner_id != request.user.id:
                return JsonResponse({"success":False, 'message':'you are not the owner of this comment'}, status=status.HTTP_401_UNAUTHORIZED)

            await sync_to_async(comment.delete)()

            return JsonResponse({"success":True, 'message':'comment deleted successfully'}, status=status.HTTP_200_OK)
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False, 'message':'something went wrong while deleting comment'}, status=status.HTTP_400_BAD_REQUEST)
