from asgiref.sync import sync_to_async
from .models import VideoModel
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import status
from utils.cloudinary import upload_image, upload_video_to_cloudinary,delete_file_from_cloudinary
from django.views.decorators.csrf import csrf_exempt
from utils.auth import verify_jwt
import traceback
from .repository import VideoRepository

# Create your views here.

# get all video with search/filter 
async def get_all_videos(request):
    if request.method == 'GET':
        page = int(request.GET.get('page',1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit
        query = request.GET.get('query', None)
        sort_by = request.GET.get('sortBy', 'created_at')
        sort_type = request.GET.get('sortType', 'desc')

        valid_sort_fields = ['created_at', 'title']
        valid_sort_types = ['asc', 'desc']

        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_type not in valid_sort_types:
            sort_type = 'desc'
        try:
            filters = Q()
            if query:
                filters &= Q(title__icontains=query)

            order_prefix = '-' if sort_type == 'desc' else ''
            order_by = f"{order_prefix}{sort_by}"
            
            videos = await VideoRepository.get_paginated_videos(filters, order_by, offset, limit)

            if not videos:
                return JsonResponse({'success': False, 'message': 'No videos found'}, status=404)
            
            total_count = await VideoRepository.getVideosTotalCound(filters)
            total_pages = (total_count + limit - 1) // limit
            # serialize data 
            data = []
            for video in videos:
                owner_data = await sync_to_async(lambda: {
                    "id": video.owner.id if video.owner else None,
                    "fullname": video.owner.fullname if video.owner else None,
                    "username": video.owner.username if video.owner else None,
                    # "avatar": video.owner.avatar if video.owner else None,
                })()
                data.append({
                "id": video.id,
                "title": video.title,
                "thumbnail": video.thumbnail,
                "url": video.video_file,
                "views": video.views,
                "duration": video.duration,
                "created_at": video.created_at,
                "owner": owner_data
                })
            
            return JsonResponse({
                    "success": True,
                    "message": "Videos fetched successfully.",
                    "data": data,
                    "total": total_count,
                    "page": int(page),
                    "limit": limit,
                    "total_pages": total_pages
                },status=200)
        
        except Exception as e:
            print(traceback.format_exc())  
            return JsonResponse({
                    "success": False,
                    "message": "Something went wrong.",
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return JsonResponse({'success':False,'message':'Method not allowd'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

# get user videos by pagination
async def get_user_videos(request,userId):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    page = request.GET.get('page',1)
    limit = request.GET.get('limit',10)
    offset = (page-1) * limit
    
    if not userId:
        return JsonResponse({'success': False, 'message': 'please give user id'}, status=400)
    
    try:
        user = await VideoRepository.fetch_user_by_userId(userId)
        if not user:
            return JsonResponse({'success': False, 'message': 'could not find the user'}, status=404)
        
        videos = await VideoRepository.fetch_user_videos(user)

        page_obj = await VideoRepository.get_paginated_videos(videos,limit,page)
        paginated_videos = page_obj['pagination_data']
        
        # serialize the data 
        data = []
        for video in paginated_videos:
            data.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "url": video.video_file if video.video_file else None,
                "thumbnail": video.thumbnail if video.thumbnail else None,
                "duration": video.duration,
                "views": video.views,
                "createdAt": video.created_at,
                'owner':{
                    'id':user.id,
                    'username':user.username,
                }
            })

        return JsonResponse({
            "success": True,
            "data": data,
            "page": page,
            "limit": limit,
            "total_pages": page_obj['total_pages'],
            "message": "Videos fetched successfully."
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
                "success": False,
                "message": "Something went wrong.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# upload videos
@csrf_exempt
@verify_jwt
async def upload_video(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    if not request.user:
        return JsonResponse({
            "success":False,
            'message':'unauthorized user'
        },status=status.HTTP_401_UNAUTHORIZED)
    
    data = request.POST
    files = request.FILES

    title = data.get('title')
    description = data.get('description')
    thumbnail = files.get('thumbnail')
    video_file = files.get('videoFile')


    if not title or not description or not thumbnail or not video_file:
        return JsonResponse({'success': False, 'message': 'Please provide all required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        thumbnail_url = await upload_image(thumbnail)
        video_file_url = await upload_video_to_cloudinary(video_file)

        thumbnail_secure_url = thumbnail_url.get('secure_url')
        video_secure_url = video_file_url.get('secure_url')
        duration = video_file_url.get('duration')

        if not thumbnail_secure_url or not video_secure_url:
            raise ValueError("Invalid response from Cloudinary.")
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "message": "Something went wrong while uploading video & thumbnail.",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    video = await VideoRepository.save_video(
        title=title,
        description=description,
        thumbnail=thumbnail_secure_url,
        video_file=video_secure_url,
        duration=duration,
        owner=request.user
    )

    return JsonResponse({
        'success': True, 
        'message': 'Video uploaded successfully',
        'video_id': video.id,
        }, 
        status=status.HTTP_201_CREATED)

# needs to work on get video details as we dont need to get comment here , we will build another api
@csrf_exempt
@verify_jwt
async def get_video_details(request, videoId):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    user = request.user 
    try:
        video = await VideoRepository.getVideoByVideoId(videoId)

        video_details = await VideoRepository.video_details(video, user)
        
        if not video_details:
            return JsonResponse({'message': 'Video not found'}, status=404)
        
        page = request.GET.get('page', 1)
        limit = request.GET.get('limit', 10)

        comments = await VideoRepository.get_video_comments(video)
        paginated_comments = await VideoRepository.get_paginated_comments(comments, limit, page)

        comment_data = [
            {
                'id': comment.id,
                'comment': comment.comment,
                "username": comment.owner.username,
                'created_at': comment.created_at
            }
            for comment in paginated_comments
        ]

        video_details['comments'] = comment_data
        video_details['pagination'] = {
            'current_page': paginated_comments.number,
            'total_pages': paginated_comments.paginator.num_pages,
            'total_comments': paginated_comments.paginator.count
        }

        return JsonResponse(video_details)
    
    except VideoModel.DoesNotExist:
        return JsonResponse({'error': 'Video not found'}, status=404)

@csrf_exempt
@verify_jwt
async def update_video_details(request,videoId):
    if request.method != 'POST':
        return JsonResponse({
      'success':False,
      'message':'Method not allowed'
        },status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not request.user:
        return JsonResponse({
      'success':False,
      'message':'Unauthorized'
        })
    
    if not videoId:
        return JsonResponse({
      'success':False,
      'message':'Pls Provide VideoId'
        },status=status.HTTP_400_BAD_REQUEST)
    
    title = request.POST.get('title')
    description = request.POST.get('description')
    thumbnail = request.FILES.get('thumbnail')

    video = await VideoRepository.fetchVideoByUserAndVideoId(videoId,request.user)

    if not video:
        return JsonResponse({
            'success':False,
            'message':'Video not found or unauthorized access'
        },status=status.HTTP_404_NOT_FOUND)
    
    try:
        if title:
            video.title = title
        
        if description:
            video.description = description
        
        oldThumbnail = video.thumbnail

        if thumbnail:
            uploaded_thumbnail = await upload_image(thumbnail)
            uploaded_thumbnail_url = uploaded_thumbnail.get('secure_url')

            video.thumbnail = uploaded_thumbnail_url

            if oldThumbnail:
                await delete_file_from_cloudinary(oldThumbnail)
        
        if not title and not description and not thumbnail:
            return JsonResponse({
                'success':False,
                'message':"video didnt updated as you didnt give anything to change"
            },status=400)
        
        await sync_to_async(video.save)()

        return JsonResponse({
            "success": True,
            "message": "Video details updated successfully"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            "success": False,
            "message": "Something went wrong while updating video details",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@verify_jwt
async def delete_video(request, videoId):
    if request.method != 'DELETE':
         return JsonResponse({
            'success': False,
            'message': 'Only DELETE method is allowed'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        
        if not videoId:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a video ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user:
            return JsonResponse({
                'success': False,
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        video = await VideoRepository.fetchVideoByUserAndVideoId(videoId, request.user)
        if not video:
            return JsonResponse({
                'success': False,
                'message': 'Video not found or unauthorized access'
            }, status=status.HTTP_404_NOT_FOUND)
        
        videoDeletedResult = await VideoRepository.deleteVideoByVideo(video)
        if videoDeletedResult:
            return JsonResponse({
            'success': True,
            'message': 'Video deleted successfully'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during video deletion',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@verify_jwt
async def toggle_publish_status(request, videoId):
    try:
        if request.method != 'PATCH':
            return JsonResponse({
                'success': False,
                'message': 'Method not allowed'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if not videoId:
            return JsonResponse({
                'success': False,
                'message': 'Please provide a video ID'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.user:
            return JsonResponse({
                'success': False,
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)

        video = await VideoRepository.fetchVideoByUserAndVideoId(videoId, request.user)
        if not video:
            return JsonResponse({
                'success': False,
                'message': 'Video not found or unauthorized access'
            }, status=status.HTTP_404_NOT_FOUND)

        video.isPublished = True
        await sync_to_async(video.save)()

        return JsonResponse({
            'success': True,
            'message': 'Video publish status toggled successfully'
        })

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
