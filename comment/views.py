from django.http import JsonResponse
from rest_framework import status
from .repository import CommentRepository
from video.repository import VideoRepository
from utils.auth import verify_jwt
from django.views.decorators.csrf import csrf_exempt
import traceback
from asgiref.sync import sync_to_async

# Create your views here.

# add comment
@csrf_exempt
@verify_jwt
async def add_comment(request,videoId):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
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
@csrf_exempt
@verify_jwt
async def get_video_comments(request,videoId) -> JsonResponse :
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not videoId:
        return JsonResponse({"success":False,'message':'pls provide video id'},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({"success":False,'message':'video doesnt exist'},status=status.HTTP_400_BAD_REQUEST)
        
        videoComments = await CommentRepository.getVideoCommentsByVideo(video,offset,limit)
        if not videoComments:
            return JsonResponse({"success":False, 'message':'no comments found'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = [{
            'id': comment.id,
            'comment': comment.comment,
            'created_at': comment.created_at,
            'likes': comment.likes.count(),
            'owner': {
                'id': comment.owner.id,
                'username': comment.owner.username
            }
        } for comment in videoComments]
        
        return JsonResponse({'success':True,'message':'successfully retreived the data','data':data}, status=status.HTTP_200_OK)
    
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False,'message':'got error while adding comment'},status=status.HTTP_400_BAD_REQUEST)


#update comment
@csrf_exempt
@verify_jwt
async def update_comment(request , commentId):
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
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
        
        if comment.owner.id != request.user.id:
            return JsonResponse({"success":False, 'message':'you are not the owner of this comment'}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment.comment = comment_text
        await sync_to_async(comment.save)()

        return JsonResponse({"success":True, 'message':'comment updated successfully'}, status=status.HTTP_200_OK)
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False, 'message':'something went wrong while updating comment'}, status=status.HTTP_400_BAD_REQUEST)


#delete comment
@csrf_exempt
@verify_jwt
async def delete_comment(request,commentId):
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    if not request.user:
        return JsonResponse({"success":False, 'message':'unauthorized user'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not commentId:
        return JsonResponse({"success":False, 'message':'pls provide comment id'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
            comment = await CommentRepository.getCommentByCommentId(commentId)
            if not comment:
                return JsonResponse({"success":False, 'message':'comment doesnt exist'}, status=status.HTTP_400_BAD_REQUEST)

            if comment.owner.id != request.user.id:
                return JsonResponse({"success":False, 'message':'you are not the owner of this comment'}, status=status.HTTP_401_UNAUTHORIZED)

            await sync_to_async(comment.delete)()

            return JsonResponse({"success":True, 'message':'comment deleted successfully'}, status=status.HTTP_200_OK)
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False, 'message':'something went wrong while deleting comment'}, status=status.HTTP_400_BAD_REQUEST)
