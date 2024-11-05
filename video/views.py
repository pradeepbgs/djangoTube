from django.shortcuts import render 
from asgiref.sync import sync_to_async
from .models import VideoModel
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from django.contrib.auth.models import User
from utils import cloudinary
from django.views.decorators.csrf import csrf_exempt
from utils.auth import verify_jwt
# Create your views here.
import traceback
from django.contrib.auth.decorators import login_required



# get all video with search/filter 
async def get_all_videos(request):
    if request.method == 'GET':
        page = request.GET.get('page',1)
        limit = int(request.GET.get('limit', 9))
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
            videos = await sync_to_async(lambda: VideoModel.objects.filter(filters).order_by(f"{order_prefix}{sort_by}"))()
            paginator = Paginator(videos, limit)
            try:
                paginated_videos = await sync_to_async(paginator.get_page)(page)
            except (EmptyPage, PageNotAnInteger):
                paginated_videos = paginator.page(1)

    # serialize data 
            data = [
                {
                    "id": video.id,
                    "title": video.title,
                    "description": video.description,
                    "thumbnail": video.thumbnail,
                    "views": video.views,
                    "duration": video.duration,
                    "is_published": video.is_published,
                    "created_at": video.created_at,
                    "updated_at": video.updated_at,
                    # Uncomment if 'owner' details are needed
                    # "owner": {
                    #     "id": video.owner.id,
                    #     "fullname": video.owner.get_full_name(),
                    #     "username": video.owner.username,
                    #     "avatar": video.owner.profile.avatar.url if video.owner.profile.avatar else None,
                    #     "coverImage": video.owner.profile.cover_image.url if video.owner.profile.cover_image else None,
                    # }
                }
                for video in paginated_videos
            ]

            return JsonResponse({
                    "success": True,
                    "message": "Videos fetched successfully.",
                    "data": data,
                    "total": paginator.count,
                    "page": int(page),
                    "limit": limit,
                    "total_pages": paginator.num_pages
                })
        except Exception as e:
            print(traceback.format_exc())  # Print the full error traceback for debugging
            return JsonResponse({
                    "success": False,
                    "message": "Something went wrong.",
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return JsonResponse({'success':False,'message':'Method not allowd'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

# get user videos by pagination

async def get_user_videos(req,userId):
    page = req.GET.get('page',1)
    limit = req.GET.get('limit',10)

    user = await sync_to_async(User.objects.filter(id=userId))()
    
    try:
        videos = VideoModel.objects.filter(owner=user).order_by('created-at')

        paginator = Paginator(videos,limit)
        try:
            paginated_videos = paginator.get_page(page)
        except (EmptyPage, PageNotAnInteger):
            paginated_videos = paginator.page(1)
        
        # serialize the data 
        data = [
            {
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "videoFile": video.videoFile.url if video.videoFile else None,
                "thumbnail": video.thumbnail.url if video.thumbnail else None,
                "duration": video.duration,
                "views": video.views,
                "createdAt": video.created_at,
                # will do in future after defining good user model
                # "owner": {
                #     "id": user.id,
                #     "username": user.username,
                #     "fullname": user.fullname,
                #     "avatar": user.profile.avatar.url if user.profile.avatar else None,
                #     "coverImage": user.profile.cover_image.url if user.profile.cover_image else None,
                # },
            } for video in paginated_videos
        ]

        return JsonResponse({
            "success": True,
            "data": data,
            "page": page,
            "limit": limit,
            "total_pages": paginator.num_pages,
            "message": "Videos fetched successfully."
        }, status=status.HTTP_200_OK)

    except:
        return JsonResponse({
                "success": False,
                "message": "Something went wrong.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@verify_jwt
async def upload_video(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    print('we eneer')
    data = request.POST
    files = request.FILES

    title = data.get('title')
    description = data.get('description')
    thumbnail = files.get('thumbnail')
    video_file = files.get('videoFile')

    # print(title,description,thumbnail,video_file)

    if not title or not description or not thumbnail or not video_file:
        return JsonResponse({'success': False, 'message': 'Please provide all required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        thumbnail_url = await cloudinary.upload_image(thumbnail)
        video_file_url = await cloudinary.upload_video(video_file)

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

    await sync_to_async(VideoModel.objects.create)(
        title=title,
        description=description,
        thumbnail=thumbnail_secure_url,
        video_file=video_secure_url,
        duration=duration,
        owner=request.user 
    )

    return JsonResponse({'success': True, 'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)