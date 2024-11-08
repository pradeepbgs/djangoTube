from django.http import JsonResponse
from rest_framework import status
from .repository import CommentRepository
from video.repository import VideoRepository
from utils.auth import verify_jwt
from django.views.decorators.csrf import csrf_exempt

import traceback

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
async def get_video_comments(request,videoId):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not videoId:
        return JsonResponse({"success":False,'message':'pls provide video id'},status=status.HTTP_400_BAD_REQUEST)
    
    try:
        page = request.GET.get('page',1)
        limit = request.GET.get('limit',10)

        video = await VideoRepository.getVideoByVideoId(videoId)
        if not video:
            return JsonResponse({"success":False,'message':'video doesnt exist'},status=status.HTTP_400_BAD_REQUEST)
        
        videoComments = await VideoRepository.getVideoCommentsByVideo(video,request.user)
        paginated_comments = await VideoRepository.get_paginated_comments(videoComments,limit,page)

        data = [{
            'id': comment.id,
            'comment': comment.comment,
            'created_at': comment.created_at,
            'likes': comment.likes_count,
            'owner': {
                'id': comment.owner.id,
                'username': comment.owner.username
            }
        } for comment in paginated_comments]
        
        return JsonResponse({'success':True,'message':'successfully retreived the data','data':data}, status=status.HTTP_200_OK)
    
    except:
        print(traceback.format_exc())
        return JsonResponse({"success":False,'message':'got error while adding comment'},status=status.HTTP_400_BAD_REQUEST)


#update comment


#delete comment